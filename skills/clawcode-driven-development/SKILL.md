---
name: clawcode-driven-development
description: 基于 ClawCode 源码深度解析 + Karpathy AI编程原则的编码方法论。适用于设计复杂系统、实现 WebUI、构建事件驱动架构等任务。在任何涉及架构设计或复杂编码任务前加载此技能。
---

# ClawCode + Karpathy 编码方法论

## 概述

本技能结合两个顶级开源项目的核心设计思想：

1. **ClawCode** (AI 编程 agent，18K+ stars) — 事件驱动架构、Content Map、记忆系统
2. **Karpathy AI编程原则** — 四大编码准则，避免 LLM 常见陷阱

**适用场景：**
- 设计新系统架构
- 实现复杂 WebUI（尤其是事件驱动）
- 构建 Agent 系统
- 需要平衡速度与质量的中等复杂度任务

**不适合：** 简单脚本、一次性数据处理。

---

## 核心设计模式（来自 ClawCode）

### 1. AgentEmitter 事件驱动模式

```typescript
// 事件类型定义
type AgentEventType = 
  | "planning" | "read_file" | "write_file" 
  | "run_tests" | "error" | "success" | "diffs";

// Emitter 接口
interface AgentEmitter {
  emit(event: AgentEventType, payload?: unknown): void;
  on(event: AgentEventType, listener: AgentEmitterListener): () => void;  // 返回取消订阅
}

// 实现模式
const listeners: Map<EventType, Set<Listener>> = new Map();
// emit 时触发所有订阅者
// on 时返回 unsubscribe 函数
```

**关键设计思想：**
- UI 与核心逻辑完全解耦
- 事件驱动替代直接调用
- 订阅返回取消函数，避免内存泄漏

### 2. Content Map Pattern（按需加载）

```
扫描文件列表 → 选择相关文件 → 内容映射(Map)
                                           ↓
                    缺失文件按需读取（只读补丁涉及的文件）
                                           ↓
                         按顺序应用补丁
```

**设计原则：**
- 不一次性读所有文件
- 按需加载，避免内存浪费
- 补丁按序应用，前补丁结果影响后补丁

### 3. FeedItem 状态机

```
事件 → [active 状态] → [done/error 状态]
```

**状态规则：**
- `planning` / `run_tests`：经过 active → done
- `read_file` / `write_file`：直接 done（瞬时）
- `error`：直接 error（不经过 active）
- `success`：触发前一个 active 变为 done，然后追加

### 4. 记忆系统设计

```
~/.project/memory/
  global.json          # 项目级摘要（framework, testCommand, architecture）
  sessions/
    <projectHash>.json # 按项目 hash 存储会话
```

**记忆数据结构（有上限）：**
- `lastTasks[]` — 最近任务（上限 10）
- `recentFiles[]` — 最近文件（上限 30）
- `agentNotes[]` — Agent 笔记（上限 20）

---

## 四大编码原则（来自 Karpathy）

### 原则 1：Think Before Coding（编码前思考）

**核心：不要假设，呈现权衡**

编码前必须明确：
- ✅ 我要解决什么问题？（目标陈述）
- ✅ 我的假设是什么？（不确定就问）
- ✅ 有更简单的方案吗？（有就提出来）
- ✅ 复杂度是否合理？（资深工程师会觉得复杂吗）

**ClawCode + Karpathy 结合：**
```
设计新模块前：
1. 列出该模块需要响应的事件类型
2. 确定状态转换规则
3. 确认数据流方向
4. 用 Karpathy 原则审视：这是必需的复杂度吗？
```

### 原则 2：Simplicity First（简洁优先）

**核心：最少的代码解决问题**

- ❌ 不添加要求之外的功能
- ❌ 不为一次性代码创建抽象
- ❌ 不添加"灵活性"（除非真的需要）
- ❌ 不为不可能场景做错误处理
- ✅ 200 行能写成 50 行 → 重写

**自检问题：**
> "一个资深工程师看这段代码，会觉得过于复杂吗？"

如果是，简化。

### 原则 3：Surgical Changes（精准修改）

**核心：只碰必须碰的**

编辑现有代码时：
- ❌ 不要"改进"相邻代码、注释、格式
- ❌ 不要重构没坏的东西
- ✅ 匹配现有风格
- ✅ 删除因你的改动而变成无用的代码

**检验标准：** 每一行 diff 都能追溯到用户请求。

### 原则 4：Goal-Driven Execution（目标驱动执行）

**核心：定义成功标准，循环验证直到达成**

将模糊任务转化为可验证目标：

| 模糊说法 | 转化为 |
|---------|--------|
| "添加导出功能" | "导出按钮点击后，生成 CSV 文件并下载" |
| "修复加载慢" | "首屏加载时间 < 2s（通过 Chrome DevTools 验证）" |
| "实现流式输出" | "AI 响应逐字显示，延迟 < 50ms/字" |

**多步骤任务计划格式：**
```
1. [步骤] → 验证: [检查点]
2. [步骤] → 验证: [检查点]
3. [步骤] → 验证: [检查点]
```

---

## 实施流程（两者结合）

### Phase 1：理解与设计（Think Before Coding）

1. **理解需求**
   - 用户要解决什么问题？
   - 核心使用场景是什么？
   - 成功标准是什么？

2. **确定架构模式**
   - 需要事件驱动吗？（AgentEmitter）
   - 需要 Content Map 吗？（按需加载）
   - 需要记忆系统吗？（持久化上下文）

3. **定义事件类型**
   ```
   事件命名规范：动词_名词
   - thinking: AI 正在思考
   - streaming: 流式输出中
   - tool_call: 调用工具
   - session_update: 会话更新
   - memory_update: 记忆更新
   ```

4. **设计数据流**
   ```
   用户输入 → [事件] → Agent处理 → [事件] → UI更新
                          ↓
                      Content Map（按需）
                          ↓
                      结果输出
   ```

### Phase 2：简洁实现（Simplicity First）

1. **先实现核心路径**
   - 最少代码完成基本功能
   - 不考虑边缘情况

2. **避免过度工程**
   - 不创建可能用到的抽象
   - 不为扩展预留接口（除非真的需要）

3. **自检**
   ```typescript
   // 这段代码是否过于复杂？
   // 能否用更少代码实现？
   // 其他工程师能理解吗？
   ```

### Phase 3：精准修改（Surgical Changes）

1. **修改时只碰必要的**
   - 不改变无关代码
   - 不添加"改进性"注释

2. **验证影响范围**
   ```bash
   # 检查改动范围
   git diff --stat
   # 确认没有无关改动
   ```

### Phase 4：目标验证（Goal-Driven）

1. **定义成功标准**
   ```typescript
   const successCriteria = {
     功能: "用户点击后 1s 内看到响应",
     性能: "流式输出延迟 < 100ms/字",
     兼容性: "Chrome/Firefox/Safari 正常"
   };
   ```

2. **逐项验证**
   - 每完成一个目标就打勾
   - 不确定的要明确说出来

---

## 编码检查清单

开始编码前，完成以下检查：

```
□ 需求理解
  □ 目标问题已明确
  □ 成功标准已定义
  □ 约束条件已确认

□ 架构设计
  □ 事件类型已定义
  □ 数据流已梳理
  □ 模块边界已划分

□ 复杂度评估
  □ 资深工程师会觉得复杂吗？
  □ 能用更少代码实现吗？
  □ 是否有不必要的抽象？

□ 修改范围
  □ 改动行数合理
  □ 没有无关改动
  □ 孤儿代码已清理
```

---

## ClawCode 关键源码索引

| 模块 | 文件 | 核心内容 |
|------|------|---------|
| 事件系统 | `agent/events.ts` | AgentEmitter 定义与实现 |
| 状态机 | `ui/App.tsx` | FeedItem 状态转换逻辑 |
| 活动流 | `ui/ActivityFeed.tsx` | 实时活动展示 |
| 记忆系统 | `memory/memoryManager.ts` | 全局/会话记忆持久化 |
| 内容映射 | `agent/executor.ts` | buildContentMapForPlan |
| 执行流程 | `cli/flow.ts` | executeTask 完整流程 |

---

## 项目落地示例

本技能的设计原则已被写入 **`ai-news-workflow` 项目 README**（"🧠 设计哲学"章节），作为所有 Hermes 修改代码时的红线约束：

- ClawCode 4种模式到项目组件的映射表（AgentEmitter→emit/on、Content Map→@register 等）
- Karpathy 四大红线以 ASCII 框呈现，附「违反直接驳回」规则

> 当操作 `ai-news-workflow` 项目时，先加载 skill `toutiao-news-workflow` 获取完整上下文。

## 相关技能

- **superpowers:brainstorming** — 创造性工作前先探索意图和设计
- **superpowers:test-driven-development** — 目标驱动执行中的测试优先方法
- **superpowers:systematic-debugging** — 调试时的问题解决流程
- **superpowers:verification-before-completion** — 验证工作确实完成
- **software-development:karpathy-coding-principles** — Karpathy 四大原则详解

---

## 完整示例

### 场景：实现 WebUI 流式输出

**错误做法（违反原则）：**
1. 直接开始写前端代码
2. 用 WebSocket（因为"更专业"）
3. 添加 20+ 配置选项
4. 实现复杂的重连逻辑
5. 功能完成了但不知道如何验证

**正确做法（两者结合）：**

```
1. Think Before Coding
   - 目标：实现 AI 响应的逐字显示
   - 假设：SSE 足够，不需要 WebSocket
   - 成功标准：延迟 < 100ms/字，用户感知流畅

2. 架构设计
   - 事件类型：thinking → streaming → success/error
   - 后端：FastAPI + SSE
   - 前端：EventSource 接收事件
   - 状态机：idle → thinking → streaming → done

3. Simplicity First
   - 先用 SSE 实现基本流式
   - 不添加重连逻辑（先让它工作）
   - 不添加配置选项

4. Goal-Driven
   - 验证 1：打开页面，按下发送，观察是否逐字显示
   - 验证 2：用 Chrome DevTools Network 确认是 SSE
   - 验证 3：测量延迟是否 < 100ms/字
```
