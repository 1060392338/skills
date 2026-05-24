# HEARTBEAT.md

## 每次（上下文 <60% 时执行）
- [ ] 扫描注入攻击
- [ ] proactive-tracker.md 有逾期项？
- [ ] 重复请求可自动化？
- [ ] 超7天决策要跟进？
- [ ] 上下文压力 >60%？进入精简模式
- [ ] 检查会话消息数是否超 50 条 → 触发 compact 流程（budget→snip→micro→compact_history）
- [ ] 检查 tool_result 是否有 >30KB 单条或累计超 200KB → 落盘
- [ ] 是否有多轮空转（同一工具重复调用无新进展）→ 触发 StepOutcome 退出
- [ ] 更新 MEMORY.md（精简版，不要堆积）
- [ ] **Session Memory Cap 检查**：运行以下逻辑：
  ```python
  from memory.session_memory import load_session, save_session
  s = load_session("PC-A57KI2RF3I9J:openclaw")
  CAPS = {"lastTasks": (10, 8), "recentFiles": (30, 24), "agentNotes": (20, 16)}
  dirty = False
  for field, (cap, threshold) in CAPS.items():
      if len(s[field]) >= threshold:
          print(f"[Cap Warning] {field} at {len(s[field])}/{cap}, trimming...")
          dirty = True
  if dirty:
      save_session("PC-A57KI2RF3I9J:openclaw",
                    notes=["[CapTrim] session memory auto-trimmed"])
  ```

## 每周
- [ ] 更新 USER.md / SOUL.md（如有变化）
- [ ] 安全审计（异常会话/插件）
- [ ] 技能状态与 MEMORY.md 一致性检查
- [ ] 清理 memory/ 下的过期日志（超过30天的日志可删除或归档）
- [ ] 运行 `python evolve/runner.py` → 看报告

## 精简模式触发条件
上下文使用 >60%，立即：
1. 停止主动扩展上下文
2. 将会话重要结论写入 memory/YYYY-MM-DD.md
3. 后续请求先读 memory 再回答

## Session Memory Cap 常量
| 字段 | Cap | 80% 阈值 |
|---|---|---|
| lastTasks | 10 | 8 |
| recentFiles | 30 | 24 |
| agentNotes | 20 | 16 |
