"""Runner — 一键运行完整进化闭环。

Observer → Analyzer → Evolver → 输出报告 + 自动更新 MEMORY.md
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
from observer import run_observer, observe_all  # noqa: E402
from analyzer import analyze, load_instincts, save_instincts, generate_recommendations  # noqa: E402


EVOLVE_DIR = Path(__file__).resolve().parent
WORKSPACE = EVOLVE_DIR.parent
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
INSTINCTS_FILE = EVOLVE_DIR / "instincts.json"
STATE_FILE = EVOLVE_DIR / "evolve-state.json"
REPORT_FILE = EVOLVE_DIR / "last-report.json"


def apply_recommendations(recs: list[dict[str, Any]], dry_run: bool = False) -> dict[str, Any]:
    """将推荐应用到 MEMORY.md。"""
    memory_updates = [r for r in recs if r["type"] == "memory_update"]
    skill_suggestions = [r for r in recs if r["type"] == "skill_suggestion"]

    if not memory_updates or dry_run:
        return {
            "applied": 0,
            "skipped": len(memory_updates) if dry_run else 0,
            "skill_suggestions": len(skill_suggestions),
            "details": "dry_run" if dry_run else "no_updates",
        }

    # 读取现有 MEMORY.md
    try:
        content = MEMORY_FILE.read_text(encoding="utf-8")
    except OSError:
        content = "# MEMORY.md\n\n"

    applied = 0
    for rec in memory_updates:
        section = rec.get("section", "经验进化")
        line = rec.get("content", "")
        if line in content:
            continue

        # 查找 section 是否存在
        section_header = f"## {section}"
        if section_header in content:
            # 追加到该 section 末尾
            idx = content.index(section_header)
            next_section = content.find("\n## ", idx + len(section_header))
            if next_section == -1:
                content = content.rstrip() + f"\n{line}\n"
            else:
                content = content[:next_section] + f"\n{line}\n" + content[next_section:]
        else:
            # 创建新 section
            content = content.rstrip() + f"\n\n## {section}\n{line}\n"
        applied += 1

    if applied > 0:
        MEMORY_FILE.write_text(content, encoding="utf-8")

    return {
        "applied": applied,
        "skill_suggestions": len(skill_suggestions),
        "suggestion_details": skill_suggestions,
    }


def run_evolution(dry_run: bool = False) -> dict[str, Any]:
    """运行完整进化闭环。"""
    now = datetime.now()

    # 1. Observer
    new_obs, state = run_observer(MEMORY_DIR, STATE_FILE)

    # 2. Analyzer
    all_obs = observe_all(MEMORY_DIR)
    existing = load_instincts(INSTINCTS_FILE)
    updated_instincts = analyze(all_obs, existing)
    save_instincts(INSTINCTS_FILE, updated_instincts)

    # 3. 生成推荐
    recs = generate_recommendations(updated_instincts)

    # 4. 应用
    apply_result = apply_recommendations(recs, dry_run=dry_run)

    # 5. 生成报告
    report = {
        "schema_version": "evolve-v1",
        "run_at": now.isoformat(),
        "dry_run": dry_run,
        "observer": {
            "new_observations": len(new_obs),
            "total_processed": len(state.get("processed_ids", [])),
            "by_category": _count_by(new_obs, "category"),
        },
        "instincts": {
            "total": len(updated_instincts),
            "high_confidence": len([i for i in updated_instincts if i.confidence >= 0.5]),
            "medium_confidence": len([i for i in updated_instincts if 0.2 <= i.confidence < 0.5]),
            "low_confidence": len([i for i in updated_instincts if i.confidence < 0.2]),
            "top_5": [
                {"id": i.id, "domain": i.domain, "confidence": i.confidence, "trigger": i.trigger[:60]}
                for i in sorted(updated_instincts, key=lambda x: -x.confidence)[:5]
            ],
        },
        "recommendations": {
            "total": len(recs),
            "memory_updates": len([r for r in recs if r["type"] == "memory_update"]),
            "skill_suggestions": len([r for r in recs if r["type"] == "skill_suggestion"]),
            "items": recs,
        },
        "apply": apply_result,
    }

    # 保存报告
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report


def _count_by(items: list, attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        key = getattr(item, attr, "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def format_report(report: dict[str, Any]) -> str:
    """格式化报告为可读文本。"""
    lines = ["🧬 经验进化报告", "=" * 30, ""]

    obs = report["observer"]
    lines.append(f"📡 观察: {obs['new_observations']} 条新 / {obs['total_processed']} 总计")
    for cat, n in obs["by_category"].items():
        lines.append(f"  • {cat}: {n}")
    lines.append("")

    inst = report["instincts"]
    lines.append(f"🧠 直觉库: {inst['total']} 条")
    lines.append(f"  高置信 ≥50%: {inst['high_confidence']}")
    lines.append(f"  中置信 20-50%: {inst['medium_confidence']}")
    lines.append(f"  低置信 <20%: {inst['low_confidence']}")

    if inst["top_5"]:
        lines.append("\n  Top 5:")
        for t in inst["top_5"]:
            lines.append(f"  [{t['confidence']:.0%}] {t['domain']}: {t['trigger']}")

    recs = report["recommendations"]
    lines.append(f"\n💡 推荐: {recs['total']} 条")
    for r in recs["items"][:5]:
        lines.append(f"  [{r['type']}] {r['content'][:70]}")

    apply_r = report["apply"]
    lines.append(f"\n✅ 应用: {apply_r['applied']} 条已写入 MEMORY.md")
    if apply_r.get("skill_suggestions"):
        lines.append(f"🎯 建议创建 {apply_r['skill_suggestions']} 个新 Skill")

    return "\n".join(lines)


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    dry = "--dry-run" in sys.argv
    report = run_evolution(dry_run=dry)
    print(format_report(report))
