# 2026-04-09 LangGraph 学习笔记

## 来源
代码路径：E:\langgraph\
文件列表（29个 .py）：

## 核心概念
- **StateGraph**：LangGraph 基本构建块，定义节点和边
- **ToolNode**：预建节点，执行模型产生的工具调用
- **MessagesState**：内置状态类型，专门存对话消息列表
- **checkpoint**：用 MemorySaver 保存执行状态，支持中断恢复
- **interrupt**：主动暂停图执行，等外部用户输入再恢复
- **Command**：恢复 interrupt 时的恢复指令，可带新数据

## 工具调用流程
1. 用 @tool 装饰器定义工具函数
2. model.bind_tools(tools) 让模型具备工具调用意识
3. 模型产生 tool_calls（意图，还没真正执行）
4. ToolNode.invoke() 真正执行工具

## 条件边
- add_conditional_edges(source, routing_fn, path_map)
- routing_fn 返回字符串（节点名）或 END

## 多智能体
- **工具交接**：用 Command(goto="agent_name") 跳转节点
- **make_handoff_tool**：工厂函数，动态生成带交接逻辑的工具
- 子图可以嵌入父图作为节点（add_node("name", subgraph)）

## 大量工具处理
- 用 vector store 做工具检索（Embedding）
- select_tools 节点根据用户 query 相似度搜索，动态选择工具

## Memory / 持久化
- MemorySaver：进程内检查点
- InMemoryStore：跨 thread 存储文档/知识
- interrupt + Command(resume=...)：实现人机交互式中断

## stream_mode
- "values"：每个步骤的完整状态
- "updates"：每个节点的增量更新

## 关键文件
- 简单使用.py：interrupt 基本用法
- Agent应用中使用.py：interrupt + Command 恢复
- 工具标准使用.py：工具审查流程
- 手动调用.py：直接调用 ToolNode
- 传递共享内存（Memory）.py：InMemoryStore 用法
- 如何构建多智能体网络.py：多 agent 交接
- 单functioncalling案例.py：OpenAI原生 function calling 完整流程
- 使用工具实现交接.py：make_handoff_tool 工厂模式
- 使用Command进行交接.py：Command.PARENT 跨图跳转
- 如何在多智能体网络添加多轮对话.py：interrupt + 多轮对话
- 无审查使用.py：自定义审查动作（continue/update/feedback）
- 重复工具选择.py：失败重试 + fallback 策略
- 如何处理大量工具.py：向量检索选工具
- 预建设ToolNode.py：create_react_agent 快速构建
