from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
TOPICS_DIR = ROOT / "topics"

SECTION_LEVEL = 3

TOPICS = {
    "perception": {
        "title": "感知",
        "keywords": [
            "感知",
            "检测",
            "分割",
            "重建",
            "detr",
            "maptr",
            "mv2dfusion",
            "daocc",
            "bev",
            "lidar",
            "point cloud",
            "点云",
            "多模态",
            "fusion",
            "occupancy",
            "3d detection",
        ],
    },
    "vla": {
        "title": "VLA",
        "keywords": [
            "vla",
            "vision-language-action",
            "具身",
            "机器人",
            "robot",
            "action",
            "policy",
            "openvla",
            "diffusion policy",
            "manipulation",
            "embodied",
        ],
    },
}


@dataclass
class Section:
    date: str
    title: str
    body: str
    source: Path
    topics: list[str]


def is_fence(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def heading_level(line: str) -> int | None:
    match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
    if not match:
        return None
    return len(match.group(1))


def heading_title(line: str) -> str:
    return re.sub(r"^#{1,6}\s+", "", line).strip()


def split_sections(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    in_fence = False

    for line in lines:
        if is_fence(line):
            in_fence = not in_fence

        level = None if in_fence else heading_level(line)
        if level == SECTION_LEVEL:
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = heading_title(line)
            current_lines = [line]
            continue

        if current_title is not None:
            if level is not None and level < SECTION_LEVEL:
                sections.append((current_title, current_lines))
                current_title = None
                current_lines = []
            else:
                current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, current_lines))

    return [(title, "\n".join(body).strip()) for title, body in sections]


def explicit_topics(text: str) -> list[str]:
    match = re.search(r"^(?:Topics?|主题|分类)\s*[:：]\s*(.+)$", text, re.M | re.I)
    if not match:
        return []

    raw_tokens = re.split(r"[,，、\s]+", match.group(1).strip().lower())
    aliases = {
        "perception": "perception",
        "感知": "perception",
        "vla": "vla",
        "具身": "vla",
    }
    topics = []
    for token in raw_tokens:
        topic = aliases.get(token)
        if topic and topic not in topics:
            topics.append(topic)
    return topics


def classify(title: str, body: str) -> list[str]:
    text = f"{title}\n{body}".lower()
    tagged = explicit_topics(text)
    if tagged:
        return tagged

    scores: dict[str, int] = {}
    for topic, config in TOPICS.items():
        scores[topic] = sum(1 for keyword in config["keywords"] if keyword.lower() in text)

    best_score = max(scores.values(), default=0)
    if best_score == 0:
        return ["uncategorized"]

    return [topic for topic, score in scores.items() if score == best_score]


def collect_sections() -> list[Section]:
    results: list[Section] = []
    for path in sorted(LOGS_DIR.glob("**/*.md")):
        if path.name.lower() == "readme.md":
            continue
        date = path.stem
        for title, body in split_sections(path):
            results.append(
                Section(
                    date=date,
                    title=title,
                    body=body,
                    source=path.relative_to(ROOT),
                    topics=classify(title, body),
                )
            )
    return results


def write_topic_file(topic: str, title: str, sections: list[Section]) -> None:
    lines = [
        f"# {title}",
        "",
        "这个文件由 `scripts/update_topic_indexes.py` 自动生成。请修改 `logs/` 下的原始日志，然后重新运行脚本。",
        "",
    ]

    if not sections:
        lines.append("暂无内容。")
    else:
        for section in sections:
            lines.extend(
                [
                    f"## {section.date} · {section.title}",
                    "",
                    f"Source: [`{section.source.as_posix()}`](../{section.source.as_posix()})",
                    "",
                    section.body,
                    "",
                    "---",
                    "",
                ]
            )

    (TOPICS_DIR / f"{topic}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_readme() -> None:
    lines = [
        "# Topics",
        "",
        "这里按主题汇总每日日志中的章节，方便不按日期阅读。",
        "",
        "- [感知](perception.md)",
        "- [VLA](vla.md)",
        "- [未分类](uncategorized.md)",
        "",
        "写日志时可以在章节内显式加标签：",
        "",
        "```markdown",
        "### 一个章节标题",
        "Topics: perception",
        "```",
        "",
        "支持的标签：`perception`、`vla`。没有标签时，脚本会用关键词做简单分类。",
    ]
    (TOPICS_DIR / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    TOPICS_DIR.mkdir(exist_ok=True)
    sections = collect_sections()

    for topic, config in TOPICS.items():
        write_topic_file(
            topic,
            config["title"],
            [section for section in sections if topic in section.topics],
        )

    write_topic_file(
        "uncategorized",
        "未分类",
        [section for section in sections if "uncategorized" in section.topics],
    )
    write_readme()


if __name__ == "__main__":
    main()
