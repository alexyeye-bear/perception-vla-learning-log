# 感知

这个文件由 `scripts/update_topic_indexes.py` 自动生成。请修改 `logs/` 下的原始日志，然后重新运行脚本。

## 2026-05-20 · maptr与DETR

Source: [`logs/2026/2026-05-20.md`](../logs/2026/2026-05-20.md)

### maptr与DETR
这个部分主要是看了知乎的回答(这里感谢 李Nik老师)，以及结合最近用到的mv2dfusion/maptr的使用上。
#### detr不需要nms
detr的一个细节是不需要nms非极大值抑制, 这是因为传统的anchor-based的方法，各个anchor是不像detr方面里面的query是存在self-att互相看到的，因此anchor会产生重复预测。
另一个原因是query的来源本身就是可学习的位置编码向量，每个query预测的区域有差异性。
#### DETR 的 Loss Function 逐项解释
DETR 会先通过 Hungarian Matching，把预测 query 和真实目标做一对一匹配；没匹配到目标的 query 会被监督为 `no object`。

几个 loss 的含义可以简化理解为：
- 分类 loss：判断 query 预测的类别是否正确，包括 `no object`。
- L1 box loss：直接约束预测框坐标和真实框坐标的数值差异。
- GIoU loss：约束预测框和真实框的空间重叠关系。
- `no object` query 只计算分类 loss，不计算 box 回归 loss。

因此 DETR 的训练目标不是让很多候选框再靠 NMS 去重，而是通过一对一匹配让每个真实目标主要对应一个 query。

#### DETR loss伪代码

```python
def detr_loss(pred_logits, pred_boxes, gt_labels, gt_boxes):
    """
    pred_logits: [num_queries, num_classes + 1]  # +1 是 no-object
    pred_boxes:  [num_queries, 4]
    gt_labels:   [num_gt]
    gt_boxes:    [num_gt, 4]
    """

    # 1. 计算每个 gt 和每个 query 之间的 matching cost
    cost_class = -softmax(pred_logits)[:, gt_labels]      # 分类代价
    cost_bbox = l1_distance(pred_boxes, gt_boxes)         # L1 框距离
    cost_giou = -generalized_iou(pred_boxes, gt_boxes)    # GIoU 越大越好，所以取负

    cost_matrix = (
        lambda_cls * cost_class
        + lambda_l1 * cost_bbox
        + lambda_giou * cost_giou
    )

    # 2. Hungarian matching，得到一对一匹配
    matched_query_idx, matched_gt_idx = hungarian_match(cost_matrix)

    # 3. 分类 target：默认所有 query 都是 no-object
    target_classes = [NO_OBJECT] * num_queries

    # 匹配到 gt 的 query 设置为对应类别
    for q, g in zip(matched_query_idx, matched_gt_idx):
        target_classes[q] = gt_labels[g]

    # 4. 分类 loss：所有 query 都参与
    loss_cls = cross_entropy(pred_logits, target_classes)

    # 5. box loss：只对匹配到 gt 的 query 计算
    matched_pred_boxes = pred_boxes[matched_query_idx]
    matched_gt_boxes = gt_boxes[matched_gt_idx]

    loss_l1 = l1_loss(matched_pred_boxes, matched_gt_boxes)
    loss_giou = giou_loss(matched_pred_boxes, matched_gt_boxes)

    # 6. 总 loss
    loss = (
        loss_cls
        + lambda_l1 * loss_l1
        + lambda_giou * loss_giou
    )

    return loss
```

---

## 2026-05-20 · 结合maptr看detr的一个应用例子

Source: [`logs/2026/2026-05-20.md`](../logs/2026/2026-05-20.md)

### 结合maptr看detr的一个应用例子

最终 query 是这样生成的：
```python
pts_embeds = self.pts_embedding.weight.unsqueeze(0)
instance_embeds = self.instance_embedding.weight.unsqueeze(1)
object_query_embeds = (pts_embeds + instance_embeds).flatten(0, 1)
```
形状是：
```python
pts_embeds.shape       = [1, num_pts_per_vec, 2C]
instance_embeds.shape  = [num_vec, 1, 2C]
pts_embeds + instance_embeds
= [num_vec, num_pts_per_vec, 2C]
flatten 后：
object_query_embeds
= [num_vec * num_pts_per_vec, 2C]
```
最终 query[i][j] = instance_query[i] + point_query[j]
例如 instance_query[0] + point_query[1] -> 第 0 个实例的第 1 个点。
针对这个实例个数*点个数的embed，maptr会把它拆成
```python
query_pos: [num_vec * num_pts, C]
query:     [num_vec * num_pts, C]
```
也就是query_pos是位置信息，用来生成reference point, query是decoder的query content
```python
learned instance embedding
        +
learned point embedding
        ↓
instance-point query
        ↓
Transformer decoder self-attention
        ↓
不同点、不同实例之间交换信息
        ↓
cross-attention 到 BEV feature
        ↓
输出每个实例的类别和点坐标
```
总结也就是，每个地图元素的每个点，都有一个query，也有一个对应的位置信息

---

## 2026-05-20 · mv2dfusion的多模态融合

Source: [`logs/2026/2026-05-20.md`](../logs/2026/2026-05-20.md)

### mv2dfusion的多模态融合
#### mix-attention
这里有一个细节，MixedCrossAttention 对所有 query 都做两次 cross-attention：
用 MultiScaleDeformableAttnFunction 去抓 image features。
用 PETRMultiheadFlashAttention / FlashMHA 去抓 point cloud features。

关键代码在 projects/mmdet3d_plugin/models/utils/mv2dfusion_transformer.py 的 MixedCrossAttention。

图像特征是
3D query reference point
-> 生成周围 key points
-> 投影到多相机 2D 图像坐标
-> 在多尺度图像特征上 deformable sampling
-> 得到图像信息
```python
# image cross-attention
weights_img = self._get_weights_img(instance_feature, query_pos, lidar2img_mat)
features_img = self.feature_sampling_img(
    feat_flatten_img,
    spatial_flatten_img,
    level_start_index_img,
    key_points,
    weights_img,
    lidar2img_mat,
    img_metas
)
output = self.output_proj_img(features_img)
output = self.drop(output) + instance_feature
其中 feature_sampling_img 里面会把 3D key points 投影到各个相机平面：

points_2d = torch.matmul(
    lidar2img_mat[:, :, None, None],
    pts_extand[:, None, ..., None]
).squeeze(-1)
points_2d = points_2d[..., :2] / points_2d[..., 2:3]

# 然后用 deformable attention 采样图像多尺度特征：

output = MultiScaleDeformableAttnFunction.apply(
    feat_flatten,
    spatial_flatten,
    level_start_index,
    points_2d,
    weights,
    self.im2col_step
)
```

点云特征由于本身就是同一个坐标系的，根据位置编码就可以有空间信息，每个 3D query 理论上都能看所有点云 token，点云 token 通常已经是稀疏 token，不是完整 dense 图像网格，数量相对可控：
当前 query feature
-> 加上 query position
-> 以点云特征 feat_flatten_pts 作为 key/value
-> 用 flash attention 做 query-to-lidar-feature attention
-> 得到点云信息
```python
# point cloud cross-attention
weights_pts = self._get_weights_pts(instance_feature, query_pos)
pts_q_pos = self.pts_q_embed(...)
pts_k_pos = self.pts_k_embed(...)
output = self.attn(
    output,
    key=feat_flatten_pts,
    value=feat_flatten_pts,
    query_pos=pts_q_pos,
    key_pos=pts_k_pos,
)
#这里的 self.attn 在 config 里配置成：

attn_cfg=dict(
    type='PETRMultiheadFlashAttention',
    batch_first=False,
    embed_dims=256,
    num_heads=8,
    dropout=0.1,
)
PETRMultiheadFlashAttention 内部又调用 FlashMHA：

self.attn = FlashMHA(embed_dims, num_heads, ...)
```

---

## 2026-05-21 · DAOcc的3d体素

Source: [`logs/2026/2026-05-21.md`](../logs/2026/2026-05-21.md)

### DAOcc的3d体素

原文里面有这么一段："  However, monocular depth estimation is inherently an ill-posed problem , while deformable attention imposes a significant computational burden. Given these limitations, we use a simple yet effective projection and sample approach similar to Harleyet al. [35]. Concretely, we first predefine a 3D voxel grid with a shape of Z ×
H/8 × W/8 , where Z represents the number of voxels along the z-axis. The center point of each voxel is then projected onto the image feature plane, and only points that fall within both the image feature plane and the camera’s field of view are retained. "
那么我们看下代码里面怎么实现这个部分的:

```python
def point_sampling(self, camera2sensor, cam2imgs, post_rots, post_trans, bda, mode='fix'):
    B, N, _, _ = camera2sensor.shape
    num_points = self.ref_3d.shape[0]

    # self.ref_3d 是预定义好的 3D voxel center，形状是 [num_points, 3]
    # 这里先扩展 batch 维度，变成 [B, num_points, 3]
    reference_points = self.ref_3d.view(1, num_points, 3) - bda[:, :3, 3].view(B, 1, 3)

    # 反向应用 LiDAR / BEV 数据增强中的旋转缩放矩阵
    # 目的是把增强后的 voxel center 还原到原始坐标系中
    reference_points = torch.inverse(
        bda[:, :3, :3].view(B, 1, 3, 3)
    ).matmul(reference_points.unsqueeze(-1))

    # 调整形状：
    # [B, num_points, 3, 1] -> [B, 1, num_points, 3]
    # 中间的 1 是为了后面 broadcast 到 N 个相机
    reference_points = reference_points.view(B, 1, num_points, 3, 1).squeeze(-1)

    # 从目标坐标系转到每个相机坐标系下
    # camera2sensor 表示 camera -> sensor 的外参
    # 所以这里通过减去平移、再乘旋转转置，把 sensor 坐标下的点变到 camera 坐标下
    reference_points = (
        reference_points - camera2sensor[:, :, :3, 3].view(B, N, 1, 3)
    ).unsqueeze(-1)

    # cam2imgs 是相机内参矩阵
    # camera2sensor[:, :, :3, :3].transpose(-1, -2) 等价于 sensor -> camera 的旋转
    # combine 组合了 sensor -> camera 和 camera -> image 的投影关系
    combine = cam2imgs.matmul(camera2sensor[:, :, :3, :3].transpose(-1, -2))

    # 把 3D voxel center 投影到相机坐标系 / 图像投影空间
    # 输出形状大致是 [B, N, num_points, 3]
    reference_points_img = combine.view(B, N, 1, 3, 3).matmul(
        reference_points
    ).squeeze(-1)

    eps = 1e-5

    # z > 0 表示点在相机前方，才可能被相机看到
    volume_mask = reference_points_img[..., 2:3] > eps

    # 透视除法：
    # [x, y, z] -> [x / z, y / z]
    # 这一步得到图像平面上的像素坐标
    reference_points_img = reference_points_img[..., 0:2] / torch.maximum(
        reference_points_img[..., 2:3],
        torch.ones_like(reference_points_img[..., 2:3]) * eps
    )

    # 应用图像增强，例如 resize、crop、flip 等
    post_rots2 = post_rots[:, :, :2, :2]
    post_trans2 = post_trans[:, :, :2]

    reference_points_img = post_rots2.view(B, N, 1, 2, 2).matmul(
        reference_points_img.unsqueeze(-1)
    )

    reference_points_img = reference_points_img.squeeze(-1) + post_trans2.view(B, N, 1, 2)

    H_in, W_in = self.input_size

    # 把像素坐标归一化到 [0, 1]
    reference_points_img[..., 0] /= W_in
    reference_points_img[..., 1] /= H_in

    # 判断投影点是否落在图像范围内
    volume_mask = (
        volume_mask
        & (reference_points_img[..., 1:2] > 0.0)
        & (reference_points_img[..., 1:2] < 1.0)
        & (reference_points_img[..., 0:1] < 1.0)
        & (reference_points_img[..., 0:1] > 0.0)
    )

    volume_mask = torch.nan_to_num(volume_mask)

    # 从 [B, N, num_points, 2] 调整成 [B, num_points, N, 2]
    # 也就是每个 voxel center 对应多个相机视角下的投影位置
    reference_points_img = reference_points_img.permute(0, 2, 1, 3)
    volume_mask = volume_mask.permute(0, 2, 1, 3)

    # mode='fix' 时，选择第一个能看到该 voxel 的相机
    # idx_camera 形状是 [B, num_points]
    idx_camera = torch.argmax(volume_mask.squeeze(-1).float(), dim=-1)

    idx_batch = torch.arange(B, dtype=torch.long, device=reference_points_img.device)
    idx_point = torch.arange(num_points, dtype=torch.long, device=reference_points_img.device)

    idx_batch = idx_batch.view(B, 1).expand(B, num_points)
    idx_point = idx_point.view(1, num_points).expand(B, num_points)

    # 根据选择出来的相机，取出每个 voxel center 在对应相机上的 2D 坐标
    reference_points_img = reference_points_img[idx_batch, idx_point, idx_camera]
    volume_mask = volume_mask[idx_batch, idx_point, idx_camera]

    # 把相机编号也编码进去，作为 grid_sample 的第三维坐标
    # 后面 BEVTransformV2 会对 [camera, H, W] 这个 3D volume 做 grid_sample
    coors_camera = idx_camera[..., None].float() / (N - 1)
    reference_points_img = torch.cat([reference_points_img, coors_camera], dim=-1)

    # reference_points_img: [B, num_points, 3]
    # 最后一维是 [u, v, camera_id_normalized]
    # volume_mask: [B, num_points, 1]，表示该 voxel 是否能被某个相机看到
    return reference_points_img, volume_mask
```

这样就得到了第i个体素应该去哪个相机的哪个位置采样

最核心可以记成：

预定义 3D voxel center
-> 还原数据增强
-> sensor 坐标转 camera 坐标
-> 相机内参投影到图像平面
-> 图像增强变换
-> 归一化到 [0, 1]
-> 选择可见相机
-> 得到每个 voxel 在图像上的采样坐标

---
