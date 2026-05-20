# Perception VLA Learning Log

个人学习日志仓库，主要记录自动驾驶感知、VLA / 具身智能模型相关的论文阅读、代码阅读、实验复现和阶段性思考。

## 方向划分

### 自动驾驶感知

关注 2D / 3D 检测、BEV 感知、多传感器融合、占用网络、车道线、轨迹预测、自动驾驶数据集与评测。

### VLA / 具身智能

关注 Vision-Language-Action 模型、机器人操作、动作表示、数据集、模仿学习、world model、VLM 到策略模型的迁移。

## 仓库结构

```text
.
├── logs/                         # 日常学习日志
│   └── 2026/
├── papers/                       # 结构化论文笔记
│   ├── autonomous-driving-perception/
│   └── vla-embodied-ai/
├── code-notes/                   # 代码阅读笔记
│   ├── perception/
│   └── vla/
├── experiments/                  # 实验、复现和小 demo 记录
│   ├── perception/
│   └── vla/
├── assets/images/                # 图片、架构图、截图
├── templates/                    # 写作模板
└── roadmap.md                    # 学习路线和主题索引
```

## 写作约定

- 日常学习记录放在 `logs/YYYY/YYYY-MM-DD.md`。
- 论文笔记按方向放到 `papers/autonomous-driving-perception/` 或 `papers/vla-embodied-ai/`。
- 代码阅读放到 `code-notes/perception/` 或 `code-notes/vla/`。
- 实验记录放到 `experiments/perception/` 或 `experiments/vla/`。
- 每篇笔记优先回答三个问题：这是什么、为什么重要、我学到了什么。

## 快速开始

复制模板开始写：

```powershell
Copy-Item templates/daily-log.md logs/2026/2026-05-20.md
Copy-Item templates/paper-note.md papers/vla-embodied-ai/openvla.md
Copy-Item templates/code-note.md code-notes/vla/openvla-code-reading.md
```

## 参考格式

- [Learning-Deep-Learning](https://github.com/patrick-llgc/Learning-Deep-Learning)
- [deeplearning-papernotes](https://github.com/dennybritz/deeplearning-papernotes)
- [Awesome-VLA](https://github.com/yueen-ma/awesome-vla)
- [Awesome-VLA-Robotics](https://github.com/Jiaaqiliu/Awesome-VLA-Robotics)
- [Large-VLM-based-VLA-for-Robotic-Manipulation](https://github.com/JiuTian-VL/Large-VLM-based-VLA-for-Robotic-Manipulation)
