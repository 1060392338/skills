# 架构借鉴笔记（2026-05-22 四仓库分析）

> 基于 evolver / GenericAgent / learn-claude-code / ruflo 四份完整源码分析的沉淀。
> 新会话启动时自动加载，指导行为。

---

## 一、Skill 管理

### 两级加载（来自 learn-claude-code s07）
- **Layer 1（启动时）**：扫描 workspace/skills/，只把 `name` + `description` 注入 SYSTEM prompt
- **Layer 2（运行时）**：需要完整内容时调用 `load_skill(name)`，通过 tool_result 注入
- 不把整篇 SKILL.md 塞进 system prompt

### 格式规范（来自 ruflo）
- 每个 SKILL.md 应声明：
  - `when_to_use` — 什么时候触发
  - `when_to_skip` — 什么时候跳过
  - type/capabilities — 功能分类和能力声明

### Skill 蒸馏（来自 evolver skill2gep.js 模式）
- 长 skill 文档可提炼为紧凑的"Gene"结构：signals_match + strategy + constraints

---

## 二、上下文管理

### 四层压缩管线（来自 learn-claude-code s08）
执行顺序不可换：budget → snip → micro → (检查 token) → compact

**L1: snip_compact** — 消息超 50 条时：
- 保留头部 3 条（初始上下文）+ 尾部 47 条（当前工作）
- 中间替换为一条占位消息

**L2: micro_compact** — 旧 tool_result 处理：
- 只保留最近 3 条 tool_result 的完整内容
- 更旧且 >120 字符的替换为 `[Previous: used {tool_name}]`
- `read_file` 结果白名单不压缩（重新读成本高）

**L3: tool_result_budget** — 大结果落盘：
- 单条 >30KB 自动写磁盘
- 上下文里留 `<persisted-output>` + 前 2000 字符预览
- 单条 user msg 所有 tool_result 总和不超 200KB

**L4: compact_history** — LLM 全量摘要：
- 前 3 层预处理后仍超阈值 → 完整对话保存到 .transcripts/
- LLM 生成摘要，保留：当前目标/关键发现/已改文件/剩余工作/用户约束
- 摘要替换全部旧消息

**熔断器**：连续 3 次失败停止重试。

### 消息输出压缩（来自 GenericAgent）
- 代码块超 6 行 → 只展前 5 行 + 行数统计
- 路径只保留文件名
- 工具参数截断到 120 字符

---

## 三、Agent Loop 设计

### StepOutcome 三态（来自 GenericAgent）
```python
StepOutcome:
  - data: Any           # 返回数据
  - next_prompt: str|None  # None → 任务完成，立即退出
  - should_exit: bool      # True → 用户中断/错误
```
- 只要工具报告 `next_prompt=None`，不再多发一轮确认
- `should_exit=True` 立即终止

### 工具路由（来自 GenericAgent dispatch 反射）
- 用 `do_{tool_name}()` 方法反射，替代 if-elif 链
- 自动注入 `_index` 和 `_tool_num`（多工具调用时的位置信息）

### Turn 计数器（来自 GenericAgent）
- 每 10 轮重置工具 schema 缓存（考虑模型端相同 schema 会缓存）
- 每 N 轮做定时注入：记忆刷新、进度检查、DANGER 警告

---

## 四、记忆系统

### 层级架构 L0-L4（来自 GenericAgent）
| 层级 | 载体 | 内容 | 典型大小 |
|------|------|------|---------|
| L0 (Meta-SOP) | AGENTS.md | 核心公理+操作规则 | ~2KB |
| L1 (Index) | memory/index.md | 极简导航索引 | <1KB |
| L2 (Facts) | MEMORY.md / session memory | 环境事实、项目摘要 | ~3KB |
| L3 (Skills) | memory/*.md | SOP、工具脚本、学习笔记 | 每个 ~3-10KB |
| L4 (Sessions) | memory/sessions/ | 原始会话日志 | 自动收集 |

### 记忆存储模式（来自 learn-claude-code s09）
- 每个记忆一个 .md 文件 + YAML frontmatter（name/description/type）
- MEMORY.md 作为索引，一行一个链接
- 索引注入 SYSTEM prompt，内容按需加载
- 记忆文件数达阈值（如 10 个）时 LLM 去重合并

### 记忆提取（来自 GenericAgent start_long_term_update）
- 完成任务后自动提炼经验
- 只存储"行动验证成功"的信息
- 四维决策树判断放哪层：
  - "环境特异性事实?" → L2
  - "通用操作规律?" → L1 [RULES]
  - "特定任务技术?" → L3 (SOP 或脚本)
  - "冗余/常识?" → 禁止存储

---

## 五、自进化（来自 evolver）

### GEP 三层资产
- **Gene**：紧凑的进化指令（category/signals_match/strategy/constraints）
- **Capsule**：成功案例胶囊
- **Event**：追加日志的进化事件

### 20 种进化信号分类（部分关键）
- `recurring_error` / `perf_bottleneck` / `capability_gap` — 问题驱动
- `user_feature_request` / `user_improvement_suggestion` — 用户驱动
- `stable_success_plateau` / `evolution_stagnation_detected` — 瓶颈驱动
- `explore_opportunity` / `curriculum_target` — 主动探索

### 进化管线
collect（收集信号）→ enrich（富化上下文）→ select（选 Gene）→ dispatch（分发指令）

---

## 六、多 Agent 编排（来自 ruflo）

### 技能分类
- 按功能分目录：orchestration/coordination/memory/swarm/planning/security/...
- 每个 skill 声明 when_to_use/when_to_skip

### 权限声明模式
- 用 glob 模式精确控制允许的命令：`Bash(npx claude-flow*)`
- 分 allow/deny 两层

---

## 七、之前对话中已设计的模式（不重复）

见 AGENTS.md Token 消耗优化节：
- 策略 1: Skill 两级加载
- 策略 2: 消息超 50 条自动摘要
- 策略 3: StepOutcome 三态退出

---

*笔记初版：2026-05-22 四仓库分析报告 *research_repos/ANALYSIS_*.md* 的提炼*
