# Learning Log

learning of perception and VLA models

个人学习日志仓库，用于记录学习内容、代码片段、实验过程和阶段性思考。

## 内容划分

### 内容一

待补充。

### 内容二

待补充。

## 仓库结构

```text
.
├── logs/                         # 日常学习日志
│   └── 2026/
├── papers/                       # 结构化论文笔记
│   ├── content-a/
│   └── content-b/
├── code-notes/                   # 代码阅读笔记
│   ├── content-a/
│   └── content-b/
├── experiments/                  # 实验、复现和小 demo 记录
│   ├── content-a/
│   └── content-b/
├── topics/                       # 从每日日志自动生成的主题索引
├── assets/images/                # 图片、架构图、截图
├── templates/                    # 写作模板
├── scripts/                      # 自动生成索引和 Git hook 脚本
└── roadmap.md                    # 学习路线和主题索引
```

## 写作约定

- 日常学习记录放在 `logs/YYYY/YYYY-MM-DD.md`。
- 论文笔记按内容放到 `papers/content-a/` 或 `papers/content-b/`。
- 代码阅读放到 `code-notes/content-a/` 或 `code-notes/content-b/`。
- 实验记录放到 `experiments/content-a/` 或 `experiments/content-b/`。
- 每篇笔记优先回答三个问题：这是什么、为什么重要、我学到了什么。
- `topics/` 由脚本自动生成，用来按主题阅读日志章节。

## 主题索引

生成主题索引：

```powershell
python scripts/update_topic_indexes.py
```

安装本地 Git hook 后，每次 `git commit` 会自动更新并暂存 `topics/`：

```powershell
.\scripts\install-git-hook.ps1
```

写日志时可以给章节加显式标签，分类会更稳定：

```markdown
### 一个章节标题
Topics: perception
```

当前支持的标签：`perception`、`vla`。没有标签时，脚本会用关键词粗略分类。

## 快速开始

复制模板开始写：

```powershell
Copy-Item templates/daily-log.md logs/2026/2026-05-20.md
Copy-Item templates/paper-note.md papers/content-a/example-paper.md
Copy-Item templates/code-note.md code-notes/content-a/example-code-reading.md
```

## 参考格式

- [Learning-Deep-Learning](https://github.com/patrick-llgc/Learning-Deep-Learning)
- [deeplearning-papernotes](https://github.com/dennybritz/deeplearning-papernotes)
