"""Observer — 扫描 memory/*.md，提取行为模式。

借鉴 ClawCode 的 observer 模块：从工具使用日志中提取重复模式。
适配 OpenClaw：从 daily memory 文件中提取错误→修复、请求→方案等模式。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Observation:
    """单条观察记录。"""
    id: str = ""
    date: str = ""
    category: str = ""  # error_fix, config_change, optimization, decision, request
    trigger: str = ""   # 触发条件描述
    action: str = ""    # 采取的行动
    outcome: str = ""   # 结果
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)
    source_file: str = ""


# 模式匹配规则
PATTERNS = [
    {
        "category": "error_fix",
        "header_re": re.compile(r"(?:问题|错误|故障|issue|error|bug|fix)", re.I),
        "section_re": re.compile(r"(?:根本原因|解决方案|修复|解决)", re.I),
    },
    {
        "category": "config_change",
        "header_re": re.compile(r"(?:配置|设置|config|setup|安装|install)", re.I),
        "section_re": re.compile(r"(?:修改|更新|添加|写入|added|updated)", re.I),
    },
    {
        "category": "optimization",
        "header_re": re.compile(r"(?:优化|性能|精简|减少|节省|optimiz|performance|improve)", re.I),
        "section_re": re.compile(r"(?:从.*到|减少|节省|提升|improved|reduced)", re.I),
    },
    {
        "category": "decision",
        "header_re": re.compile(r"(?:决定|选择|方案|决策|decision|chose|selected)", re.I),
        "section_re": re.compile(r"(?:原因|理由|because|reason|why)", re.I),
    },
    {
        "category": "request",
        "header_re": re.compile(r"(?:待办|TODO|todo|需要|待完成|pending)", re.I),
        "section_re": None,
    },
]


def _extract_sections(text: str) -> list[dict[str, str]]:
    """将 markdown 按 ## 和 ### 分节。"""
    sections: list[dict[str, str]] = []
    current_title = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        m = re.match(r"^(#{2,3})\s+(.+)", line)
        if m:
            if current_title or current_lines:
                sections.append({
                    "title": current_title,
                    "body": "\n".join(current_lines).strip(),
                })
            current_title = m.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title or current_lines:
        sections.append({
            "title": current_title,
            "body": "\n".join(current_lines).strip(),
        })
    return sections


def _make_observation_id(date: str, category: str, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:30]
    return f"{date}-{category}-{slug}"


def observe_file(filepath: Path) -> list[Observation]:
    """从单个 memory 文件提取观察。"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError:
        return []

    date_str = filepath.stem  # e.g. 2026-04-03
    sections = _extract_sections(text)
    observations: list[Observation] = []

    for sec in sections:
        title = sec["title"]
        body = sec["body"]
        if not body.strip():
            continue

        for pat in PATTERNS:
            if not pat["header_re"].search(title):
                continue
            # 提取触发/行动/结果
            trigger = title
            action_lines: list[str] = []
            outcome_lines: list[str] = []
            current_bucket = "action"

            for bline in body.splitlines():
                bline = bline.strip()
                if not bline:
                    continue
                # 检测结果段落
                if pat["section_re"] and pat["section_re"].search(bline):
                    current_bucket = "outcome"
                if current_bucket == "outcome":
                    outcome_lines.append(bline.lstrip("- "))
                else:
                    action_lines.append(bline.lstrip("- "))

            if not action_lines:
                action_lines = [body[:200]]

            # 提取标签
            tags: list[str] = []
            tag_matches = re.findall(r"(?:飞书|feishu|微信|wechat|skills?|memory|heartbeat|config|api|模型|model)", body, re.I)
            tags.extend(set(t.lower() for t in tag_matches))

            obs = Observation(
                id=_make_observation_id(date_str, pat["category"], title),
                date=date_str,
                category=pat["category"],
                trigger=trigger,
                action=" | ".join(action_lines[:3]),
                outcome=" | ".join(outcome_lines[:3]) if outcome_lines else "unknown",
                confidence=0.5,
                tags=tags,
                source_file=str(filepath),
            )
            observations.append(obs)
            break  # 一个 section 只匹配一个 category

    return observations


def observe_all(memory_dir: Path, since_date: str = "") -> list[Observation]:
    """扫描所有 memory 文件。"""
    all_obs: list[Observation] = []
    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.stem < since_date:
            continue
        all_obs.extend(observe_file(md_file))
    return all_obs


def load_state(state_path: Path) -> dict[str, Any]:
    """加载运行状态。"""
    if not state_path.exists():
        return {"last_scan_date": "", "processed_ids": []}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {"last_scan_date": "", "processed_ids": []}


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run_observer(memory_dir: Path, state_path: Path) -> tuple[list[Observation], dict[str, Any]]:
    """运行观察器，返回新观察和更新后的状态。"""
    state = load_state(state_path)
    since = state.get("last_scan_date", "")
    processed = set(state.get("processed_ids", []))

    all_obs = observe_all(memory_dir, since_date=since)
    new_obs = [o for o in all_obs if o.id not in processed]

    state["last_scan_date"] = datetime.now().strftime("%Y-%m-%d")
    state["processed_ids"] = list(processed | {o.id for o in new_obs})
    # 限制保留的 ID 数量
    if len(state["processed_ids"]) > 500:
        state["processed_ids"] = state["processed_ids"][-500:]

    save_state(state_path, state)
    return new_obs, state


if __name__ == "__main__":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ws = Path(__file__).resolve().parent.parent
    memory_dir = ws / "memory"
    state_path = Path(__file__).resolve().parent / "evolve-state.json"

    obs, state = run_observer(memory_dir, state_path)
    print(f"发现 {len(obs)} 条新观察 (总计处理 {len(state.get('processed_ids', []))} 条)")
    for o in obs:
        print(f"  [{o.category}] {o.trigger[:60]} → {o.outcome[:60]}")
