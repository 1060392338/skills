"""
Session Memory Manager（参考 ClawCode memoryManager.ts 设计）

持久化结构：
  memory/sessions/<hash>.json → session memory
  memory/global.json           → 全局记忆（项目摘要、设置）

Session Memory 结构：
  - lastTasks: 最近任务（cap 10）
  - recentFiles: 最近访问/修改的文件（cap 30）
  - agentNotes: agent 笔记（cap 20）

用法：
  from session_memory import load_session, save_session, build_context
  session = load_session("default")
  save_session("default", task="xxx", files=[...])
  ctx = build_context("default")
"""

import json
import os
import hashlib
from pathlib import Path
from typing import Optional

BASE = Path(__file__).parent
SESSIONS_DIR = BASE / "sessions"
GLOBAL_FILE = BASE / "global.json"

MAX_LAST_TASKS = 10
MAX_RECENT_FILES = 30
MAX_AGENT_NOTES = 20

# ── helpers ──────────────────────────────────────────────────────────────────

def _ensure_dirs():
    SESSIONS_DIR.mkdir(exist_ok=True)
    if not GLOBAL_FILE.exists():
        GLOBAL_FILE.write_text(json.dumps({"projectSummaries": {}}, ensure_ascii=False))

def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def _save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _cap(arr: list, max_: int) -> list:
    return arr[:max_]

# ── session memory ───────────────────────────────────────────────────────────

def load_session(root: str = "default") -> dict:
    """加载 session memory，root 是项目标识（如 'main' / 'clawcode' 等）"""
    _ensure_dirs()
    path = SESSIONS_DIR / f"{_hash(root)}.json"
    data = _load_json(path, {
        "lastTasks": [],
        "recentFiles": [],
        "agentNotes": [],
    })
    return {
        "lastTasks": _cap(data.get("lastTasks", []), MAX_LAST_TASKS),
        "recentFiles": _cap(data.get("recentFiles", []), MAX_RECENT_FILES),
        "agentNotes": _cap(data.get("agentNotes", []), MAX_AGENT_NOTES),
    }

def save_session(
    root: str = "default",
    task: Optional[str] = None,
    files: Optional[list[str]] = None,
    notes: Optional[list[str]] = None,
):
    """
    每次任务完成后调用，追加/裁切 session 数据并写盘。
    - task: 本次任务描述
    - files: 本次访问/修改的文件路径列表
    - notes: agent 笔记（如教训、决策、发现）
    """
    _ensure_dirs()
    path = SESSIONS_DIR / f"{_hash(root)}.json"
    sess = load_session(root)

    if task:
        # task 去重后置顶
        tasks = [task] + [t for t in sess["lastTasks"] if t != task]
        sess["lastTasks"] = _cap(tasks, MAX_LAST_TASKS)

    if files:
        # files 去重，files 在前（更新的在前）
        seen = set(sess["recentFiles"])
        merged = files + [f for f in sess["recentFiles"] if f not in seen]
        sess["recentFiles"] = _cap(merged, MAX_RECENT_FILES)

    if notes:
        notes_list = notes + sess["agentNotes"]
        sess["agentNotes"] = _cap(notes_list, MAX_AGENT_NOTES)

    _save_json(path, sess)

# ── global memory ───────────────────────────────────────────────────────────

def load_global() -> dict:
    _ensure_dirs()
    return _load_json(GLOBAL_FILE, {"projectSummaries": {}})

def save_project_summary(project_key: str, summary: dict):
    """保存项目摘要：framework / testCommand / architecture"""
    _ensure_dirs()
    global_ = load_global()
    existing = global_.get("projectSummaries", {}).get(project_key, {
        "framework": "", "testCommand": "", "architecture": ""
    })
    global_["projectSummaries"][project_key] = {**existing, **summary}
    _save_json(GLOBAL_FILE, global_)

# ── context building ─────────────────────────────────────────────────────────

def build_context(root: str = "default") -> str:
    """
    把 global + session memory 拼接成一段 prompt 可用的上下文字符串。
    如果没有任何记忆，返回空字符串。
    """
    global_ = load_global()
    sess = load_session(root)
    parts = []

    summary = global_.get("projectSummaries", {}).get(root)
    if summary:
        parts.append(
            f"Project: framework={summary.get('framework','?')} | "
            f"testCommand={summary.get('testCommand','?')} | "
            f"architecture={summary.get('architecture','?')}"
        )

    if sess["lastTasks"]:
        parts.append("Recent tasks: " + "; ".join(sess["lastTasks"][:5]))

    if sess["recentFiles"]:
        parts.append("Recent files: " + ", ".join(sess["recentFiles"][:10]))

    if sess["agentNotes"]:
        parts.append("Agent notes: " + "; ".join(sess["agentNotes"][:5]))

    if not parts:
        return ""
    return "\n\n[Session Memory]\n" + "\n".join(parts) + "\n"

# ── quick demo ────────────────────────────────────────────────────────────────

# ── Context Selection: 文件 relevance scoring ───────────────────────────────

def score_files(
    root: str = "default",
    query: str = "",
    max_files: int = 12,
    max_chars: int = 18000,
) -> list[tuple[str, int, int]]:
    """
    基于当前任务 query，对 recentFiles 做 relevance scoring，
    返回截断后的文件列表（path, score, approx_chars）。
    
    评分逻辑：
    - query 关键词命中文件名 → +10/次
    - query 关键词命中路径 → +3/次  
    - 最近访问的文件（index 靠前）→ +len-index 衰减
    - 目录优先级：projects > memory > src > 其他
    
    截断策略：
    - 文件数上限：max_files（默认 12）
    - 总字符数上限：max_chars（默认 18000）
    - 满足任一条件即停止
    """
    import re
    from pathlib import Path
    
    sess = load_session(root)
    files = sess.get("recentFiles", [])
    if not files:
        return []
    
    query_words = query.lower().split() if query else []
    
    # 目录优先级映射
    PRIORITY_DIRS = {
        "projects": 5, "src": 4, "memory": 3,
        "skills": 2, "utils": 1,
    }
    
    def get_dir_priority(path: str) -> int:
        for d, p in PRIORITY_DIRS.items():
            if d in path.lower():
                return p
        return 0
    
    def estimate_chars(path: str) -> int:
        p = Path(path)
        if p.exists() and p.is_file():
            try:
                return min(p.stat().st_size, 5000)
            except Exception:
                pass
        return 1000  # 默认估算
    
    scored = []
    for idx, fpath in enumerate(files):
        score = 0
        fpath_lower = fpath.lower()
        
        # 关键词命中
        for word in query_words:
            if word in fpath_lower:
                score += 10
        
        # 路径命中（权重更低）
        for word in query_words:
            if word in fpath_lower.replace("\\", "/"):
                score += 3
        
        # 顺序衰减（最新的文件排前面，分数更高）
        recency_score = max(0, len(files) - idx - 1)
        score += recency_score
        
        # 目录优先级
        score += get_dir_priority(fpath)
        
        approx_chars = estimate_chars(fpath)
        scored.append((fpath, score, approx_chars))
    
    # 按 score 降序排列
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # 截断：文件数 + 字符数双限
    selected = []
    total_chars = 0
    for fpath, score, chars in scored:
        if len(selected) >= max_files:
            break
        if total_chars + chars > max_chars:
            break
        selected.append((fpath, score, chars))
        total_chars += chars
    
    return selected


# ── quick demo ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # demo
    save_session("test", task="分析 LangGraph 代码", files=["a.py","b.py"], notes=["发现子图用法"])
    ctx = build_context("test")
    print(ctx)
    print("session:", load_session("test"))
    ranked = score_files("test", query="langgraph python")
    print("ranked files:", ranked)
