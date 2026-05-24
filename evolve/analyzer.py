"""Analyzer — 聚类观察为直觉，计算置信度。

借鉴 ClawCode 的 learning/analyzer.py + quality.py：
- 按 category + tags 聚类
- 置信度 = f(次数, 成功率, 时间衰减)
- 冲突检测
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from observer import Observation


@dataclass
class Instinct:
    """一条直觉：从多次观察中提炼的行为规则。"""
    id: str = ""
    domain: str = ""          # error_fix, config_change, optimization, decision, request
    trigger: str = ""         # 触发条件
    action: str = ""          # 建议行动
    confidence: float = 0.0   # 0.0 ~ 1.0
    evidence_count: int = 0   # 支撑观察数
    success_count: int = 0    # 成功次数
    failure_count: int = 0    # 失败次数
    first_seen: str = ""
    last_seen: str = ""
    tags: list[str] = field(default_factory=list)
    related_ids: list[str] = field(default_factory=list)  # 关联观察 ID
    updated_at: str = ""


def load_instincts(path: Path) -> list[Instinct]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Instinct(**i) for i in data.get("instincts", [])]
    except Exception:
        return []


def save_instincts(path: Path, instincts: list[Instinct]) -> None:
    path.write_text(
        json.dumps(
            {"version": 1, "instincts": [asdict(i) for i in instincts], "updated_at": datetime.now().isoformat()},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )


def _similarity(a: str, b: str) -> float:
    """简单文本相似度（Jaccard on word bigrams）。"""
    def bigrams(s: str) -> set[str]:
        words = re.findall(r"[\w\u4e00-\u9fff]+", s.lower())
        return {f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)} if len(words) > 1 else set(words)

    sa, sb = bigrams(a), bigrams(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _make_instinct_id(domain: str, trigger: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", trigger.lower()).strip("-")[:40]
    return f"{domain}-{slug}"


def _compute_confidence(evidence_count: int, success_count: int, failure_count: int, days_since_last: float) -> float:
    """置信度 = 基础分 × 衰减因子。

    基础分 = 成功率 × log2(证据数+1) / 4  （归一化到 0~1）
    衰减 = e^(-days/30)   （30天半衰期）
    """
    total = success_count + failure_count
    if total == 0:
        base = 0.3
    else:
        success_rate = success_count / total
        base = success_rate * min(1.0, math.log2(evidence_count + 1) / 4.0)

    decay = math.exp(-days_since_last / 30.0)
    return round(max(0.05, min(1.0, base * decay)), 4)


def _cluster_observations(observations: list[Observation]) -> dict[str, list[Observation]]:
    """按 category 聚类，同一 category 内按 trigger 相似度合并。"""
    by_cat: dict[str, list[Observation]] = {}
    for obs in observations:
        by_cat.setdefault(obs.category, []).append(obs)

    clusters: dict[str, list[Observation]] = {}
    for cat, obs_list in by_cat.items():
        merged: list[list[Observation]] = []
        for obs in obs_list:
            placed = False
            for group in merged:
                if any(_similarity(obs.trigger, g.trigger) > 0.3 for g in group):
                    group.append(obs)
                    placed = True
                    break
            if not placed:
                merged.append([obs])
        for i, group in enumerate(merged):
            key = f"{cat}-{i}"
            clusters[key] = group
    return clusters


def analyze(observations: list[Observation], existing: list[Instinct]) -> list[Instinct]:
    """将新观察融合到直觉库。"""
    now = datetime.now()
    clusters = _cluster_observations(observations)

    # 建立现有直觉索引
    existing_by_id = {i.id: i for i in existing}
    result = list(existing)

    for cluster_key, obs_list in clusters.items():
        # 取第一个观察的 trigger 作为代表
        rep = obs_list[0]
        instinct_id = _make_instinct_id(rep.category, rep.trigger)

        # 检查是否与已有直觉相似
        matched: Instinct | None = None
        for inst in result:
            if inst.domain == rep.category and _similarity(inst.trigger, rep.trigger) > 0.3:
                matched = inst
                break

        if matched:
            # 更新已有直觉
            matched.evidence_count += len(obs_list)
            matched.success_count += sum(1 for o in obs_list if o.outcome and o.outcome != "unknown")
            matched.failure_count += sum(1 for o in obs_list if o.outcome == "unknown")
            matched.last_seen = max(matched.last_seen, rep.date)
            matched.related_ids.extend([o.id for o in obs_list if o.id not in matched.related_ids])
            matched.tags = list(set(matched.tags + [t for o in obs_list for t in o.tags]))
            # 更新行动描述（取最新的）
            if rep.action:
                matched.action = rep.action

            days_since = (now - datetime.fromisoformat(matched.last_seen)).days if matched.last_seen else 0
            matched.confidence = _compute_confidence(
                matched.evidence_count, matched.success_count, matched.failure_count, days_since
            )
            matched.updated_at = now.isoformat()
        else:
            # 创建新直觉
            success = sum(1 for o in obs_list if o.outcome and o.outcome != "unknown")
            failure = sum(1 for o in obs_list if o.outcome == "unknown")
            tags = list(set(t for o in obs_list for t in o.tags))

            inst = Instinct(
                id=instinct_id,
                domain=rep.category,
                trigger=rep.trigger,
                action=rep.action,
                confidence=_compute_confidence(len(obs_list), success, failure, 0),
                evidence_count=len(obs_list),
                success_count=success,
                failure_count=failure,
                first_seen=rep.date,
                last_seen=rep.date,
                tags=tags,
                related_ids=[o.id for o in obs_list],
                updated_at=now.isoformat(),
            )
            result.append(inst)

    # 对已有直觉做衰减（没有新观察支撑的）
    for inst in result:
        if inst.last_seen:
            days_since = (now - datetime.fromisoformat(inst.last_seen)).days
            inst.confidence = _compute_confidence(
                inst.evidence_count, inst.success_count, inst.failure_count, days_since
            )

    return result


def generate_recommendations(instincts: list[Instinct], min_confidence: float = 0.3) -> list[dict[str, Any]]:
    """生成推荐：高置信度直觉 → MEMORY.md 更新建议 / Skill 建议。"""
    recs: list[dict[str, Any]] = []
    for inst in sorted(instincts, key=lambda x: -x.confidence):
        if inst.confidence < min_confidence:
            continue

        if inst.domain == "error_fix":
            recs.append({
                "type": "memory_update",
                "section": "常见问题",
                "content": f"- **{inst.trigger}**: {inst.action} (置信度 {inst.confidence:.0%}, {inst.evidence_count}次验证)",
                "instinct_id": inst.id,
                "confidence": inst.confidence,
            })
        elif inst.domain == "optimization":
            recs.append({
                "type": "memory_update",
                "section": "已优化",
                "content": f"- {inst.trigger}: {inst.action} (效果 {inst.confidence:.0%})",
                "instinct_id": inst.id,
                "confidence": inst.confidence,
            })
        elif inst.domain == "config_change":
            recs.append({
                "type": "memory_update",
                "section": "配置备忘",
                "content": f"- {inst.trigger}: {inst.action}",
                "instinct_id": inst.id,
                "confidence": inst.confidence,
            })
        elif inst.domain == "request" and inst.evidence_count >= 2:
            recs.append({
                "type": "skill_suggestion",
                "content": f"重复任务 '{inst.trigger}' 出现 {inst.evidence_count} 次，建议创建自动化 Skill",
                "instinct_id": inst.id,
                "confidence": inst.confidence,
            })

    return recs


if __name__ == "__main__":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from observer import observe_all, load_state  # noqa: E402

    ws = Path(__file__).resolve().parent.parent
    memory_dir = ws / "memory"
    instincts_path = Path(__file__).resolve().parent / "instincts.json"

    obs = observe_all(memory_dir)
    existing = load_instincts(instincts_path)
    updated = analyze(obs, existing)
    save_instincts(instincts_path, updated)

    print(f"直觉库: {len(updated)} 条")
    for inst in sorted(updated, key=lambda x: -x.confidence)[:10]:
        print(f"  [{inst.confidence:.0%}] {inst.domain}: {inst.trigger[:50]}")

    recs = generate_recommendations(updated)
    if recs:
        print(f"\n推荐 ({len(recs)} 条):")
        for r in recs:
            print(f"  [{r['type']}] {r['content'][:80]}")
