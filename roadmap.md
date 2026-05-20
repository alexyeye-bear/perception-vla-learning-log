# Roadmap

这个文件用于维护长期学习路线、主题索引和阶段性目标。

## 1. 自动驾驶感知

### 核心主题

- 2D / 3D object detection
- LiDAR-only perception
- Camera-only BEV perception
- Multi-modal fusion
- Occupancy prediction
- Tracking and motion prediction
- Dataset and benchmark: KITTI, nuScenes, Waymo, Argoverse

### 推荐记录顺序

1. 数据集与坐标系：先理解传感器、标定、坐标变换和评测指标。
2. 单模态基线：分别阅读 camera-only、LiDAR-only 代表方法。
3. BEV 表示：重点理解 Lift-Splat、Transformer BEV、query-based 方法。
4. 多模态融合：记录 early / middle / late fusion 的区别。
5. Occupancy 与世界模型：为后续 VLA 和 embodied AI 衔接做准备。

## 2. VLA / 具身智能

### 核心主题

- Vision-Language-Action model
- Robot manipulation
- Action representation and action tokenizer
- Imitation learning
- Diffusion policy
- Open X-Embodiment / RLDS
- VLM grounding and planning
- World model and embodied reasoning

### 推荐记录顺序

1. 先读 survey / awesome list，建立模型谱系。
2. 阅读 mini-VLA 这类最小实现，理解 image-text-state-action 的基本流动。
3. 阅读 OpenVLA，重点记录数据格式、模型结构、微调方式和推理接口。
4. 横向比较动作表示：离散 action token、连续控制、diffusion policy。
5. 记录 VLA 和自动驾驶感知的连接点：场景理解、时序建模、规划与控制。

## 3. 每周维护

- 每周至少整理 1 篇论文笔记。
- 每周至少写 1 篇日常学习日志。
- 每两周更新一次 README 索引。
- 每完成一个实验，记录环境、命令、结果和失败原因。

## 4. 待补充索引

### 论文笔记

- 自动驾驶感知：
- VLA / 具身智能：

### 代码阅读

- 自动驾驶感知：
- VLA / 具身智能：

### 实验记录

- 自动驾驶感知：
- VLA / 具身智能：
