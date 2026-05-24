# AGENTS.md — Agent 工作规范（ClawCode 驱动）

## 启动序列

每次会话：
1. 读 MEMORY.md → 加载 global + session memory
2. session_memory.py → `load_session(root)` 获取 lastTasks / recentFiles / agentNotes
3. 读 SOUL.md、USER.md（如有）
4. 根据 session memory 构建 context string（`build_context(root)`）

## 记忆

- **长期（global）**: MEMORY.md ≈ ClawCode global.json
- **会话（session）**: `memory/sessions/<hash>.json`（session_memory.py 管理）
  - root = "PC-A57KI2RF3I9J:openclaw"
  - lastTasks（cap 10）/ recentFiles（cap 30）/ agentNotes（cap 20）
- **每日日志**: `memory/YYYY-MM-DD.md`
- **说了要记的事** → 写文件，不要靠"记住"

## 任务完成后（强制）

**以下任一条件触发时，必须立即调用 `save_session()`**：
- 一个可独立交付的子任务完成时
- 会话结束前（最后一条回复前）
- 主动暂停/终止任务时
- 心跳触发且有实质性新进展时

```python
from memory.session_memory import save_session
save_session(
    root="PC-A57KI2RF3I9J:openclaw",
    task="任务描述",
    files=["修改过的文件路径"],
    notes=["教训/发现/决策"]
)
```

**不要等全部完成再调用** — 每批输出后立即调用，哪怕整件事还没收尾。

## 红线

- 不外泄私密数据
- 破坏性操作先问
- `trash` > `rm`
- 不确定就问
- **大任务必须分批输出，不等全部完成**
- **超过 10 分钟无输出 → 停止，告知进度和卡点**

## 群聊

该说才说：被@、能加值、纠正错误。质量 > 数量。

## 工具 & 技能策略

- SKILL.md：需要时才读，读完即用
- 工具：先用现成的，少用 exec hop
- skill 目录：`~/.openclaw/skills/` 和 `~/.agents/skills/`

## Heartbeat

收到心跳时：
1. 读 HEARTBEAT.md 并执行
2. 调用 `load_session()` 检查 session memory cap 状态
3. 如果任何数组超过 cap 的 80%，触发裁切并 save_session

## 任务工作流（ClawCode 驱动）

1. **蓝图**：说清目标 / 约束 / 验收标准
2. **风险识别**：性能 / 安全 / 可靠性隐患
3. **最小实现**：最简单的架构满足需求
4. **分批执行**：大任务切块，每块完成后立即输出结果
5. **Plan → Apply 分离**：规划归规划，确认后再 apply
6. **权衡报告**：改了什么 / 放弃了什么 / 什么未验证
7. **强制 save_session**：任务完成后必须调用 save_session

## Token 消耗优化

### 核心策略
- 不回答不相关的问题
- 不引用不相关的上下文，仅在需要时查找
- 渐进式披露：先结论后细节，用户追问再展开
- **上下文 >60% 立即停手，结论写入 memory，压缩上下文**

### 策略 1: Skill 两级加载（按需加载）
参考：learn-claude-code s07
- **Layer 1（启动时）**：扫描 `workspace/skills/` 目录，只把每个 SKILL.md 的 `name` + `description` 注入 SYSTEM prompt（每 skill ~100 tokens）
- **Layer 2（运行时）**：需要某个 skill 的完整内容时，调用 `load_skill(name)` 工具，通过 tool_result 注入
- **坚决不把整篇 SKILL.md 塞进 system prompt**
- 每个 SKILL.md 应声明 `when_to_use` / `when_to_skip`（参考 ruflo 规范）

### 策略 2: 消息超 50 条自动摘要
参考：learn-claude-code s08
- 会话消息数超过 50 条时，执行 compact 流程（**顺序不可换**）：
  1. `tool_result_budget`（L3）：单条 tool_result >30KB 落盘到 `.task_outputs/tool-results/`，上下文只留 `<persisted-output>` + 前 2000 字符；同条 user msg 所有 tool_result 总和不超 200KB
  2. `snip_compact`（L1）：保留头部 3 条（初始上下文）+ 尾部 47 条（当前工作），裁掉中间
  3. `micro_compact`（L2）：旧 tool_result 内容（>120 字符且非最近 3 条）替换为 `[Previous: used {tool_name}]`，`read_file` 结果不压缩
  4. 如果 token 仍超阈值 → `compact_history`: 保存完整 transcript 到 memory/transcripts/，LLM 生成摘要替换全部旧消息
- LLM 输出压缩（参考 GenericAgent）：代码块 >6 行只展前 5 行，路径只留文件名，工具参数截 120 字符
- 熔断器：compact_history 连续失败 3 次停止重试

### 策略 3: StepOutcome 三态自动退出
参考：GenericAgent agent_loop.py
- 工具调用返回 `StepOutcome(data, next_prompt, should_exit)` 三态：
  - `next_prompt=None` → 当前任务完成，立即退出循环（省掉末尾空转）
  - `should_exit=True` → 用户中断/错误，立即终止
  - 非空 next_prompt → 继续下一轮
- **只要工具报告任务完成，不再多发一轮确认**

### 策略 4: Turn 计数器 + 缓存
参考：GenericAgent llmcore.py
- 每 10 轮刷新一次工具 schema（模型端已有缓存的不要重复发）
- 每 N 轮做定时注入：记忆刷新、进度检查
