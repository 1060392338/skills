# 🔬 经验进化系统 (Evolve)

从 ClawCode 源码移植的核心能力：**观察 → 直觉 → 进化** 闭环。

## 工作原理

```
Daily Memory → Observer → Patterns → Instincts → Recommendations → MEMORY.md / Skills
```

1. **Observer** — 扫描 `memory/*.md`，提取行为模式
2. **Analyzer** — 聚类重复模式，计算置信度
3. **Evolver** — 生成推荐，更新 MEMORY.md / 建议新 Skill

## 文件结构

- `instincts.json` — 直觉数据库（模式 + 置信度 + 计数）
- `evolve-state.json` — 运行状态（上次扫描位置）
- `observer.py` — 模式提取器
- `analyzer.py` — 聚类与置信度计算
- `runner.py` — 一键运行完整闭环

## 用法

```bash
python evolve/runner.py
```

或在 HEARTBEAT.md 中加入检查项自动触发。

## 借鉴 ClawCode 的关键设计

- **置信度衰减**: 模式随时间衰减，避免过时建议
- **冲突检测**: 新模式与旧模式矛盾时标记冲突
- **体验胶囊**: 结构化经验包（问题→步骤→迁移规则）
- **质量门控**: 进化内容上线前自动检查
