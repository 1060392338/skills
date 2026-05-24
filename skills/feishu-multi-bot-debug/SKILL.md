---
name: feishu-multi-bot-debug
description: Debug and coordinate multiple Feishu bots in a group chat - setup, whitelist, inter-bot communication
---

# Feishu Multi-Bot Debug & Coordination

## 背景
飞书群里有多个 bot（主bot + 子bot），需要实现：
1. 互相感知（被动接收消息）
2. 主动协作（@其他bot）

## Bot 信息

| Bot | AppID | OpenID |
|-----|-------|--------|
| **Hermes（主bot/我）** | `cli_a960a49baef99bdd` | `ou_8a17e9f2b804647a9d9af73ae0f6d9c0` |
| **openclaw** | `cli_a927388202b89cc8` | `ou_cd468a4ab7bc50207d50612e7c189e83` |
| **mac** | `cli_a956d74d8b389bc2` | `ou_73bb5a7d5c14fbf5b2d2df1610be2b37` |

## 关键配置

```
FEISHU_ALLOWED_USERS=ou_1122210fb81365e5a8bb203286e96e65,ou_cd468a4ab7bc50207d50612e7c189e83,ou_73bb5a7d5c14fbf5b2d2df1610be2b37,ou_8a17e9f2b804647a9d9af73ae0f6d9c0
```

**注意：修改后需要 gateway 重启生效**

## 飞书平台限制（重要）

- bot **只能收到被@的消息**，不能被动接收所有群消息
- bot 发消息（不@任何人）→ 其他 bot **收不到**
- bot 之间必须通过 **@目标bot** 才能触发响应
- bot 不能给另一个 bot 发 DM（会报 `Bot has NO availability to this user`）

## 排查步骤

1. **查群成员**: `POST /open-apis/im/v1/chats/{chat_id}/members` with member_id_type=open_id
2. **查 bot 消息记录**: 看 inbound 日志确认是否收到
3. **白名单问题**: 检查 FEISHU_ALLOWED_USERS 是否包含发送者的 open_id
4. **发消息测试**: 用 `POST /open-apis/im/v1/messages` 发到群（需有效 tenant_access_token）

## 共享文档协作

- 文档 ID: `CI6CdwGUOoCgBXxKS7cMt7Bnaf`
- 用于记录 bot 协作日志，让所有 bot 共享上下文

## Bot 间上下文共享

**问题**：多 bot 在同一群，各自只能收到 @自己的消息，不知道对方和用户聊过什么，无法接上上下文。

**方案对比**：

| 方案 | 可行性 | 用户体验 |
|------|--------|----------|
| 共享 Markdown 文件（`~/.hermes/shared-memory.md`） | ✅ 已实现 | ❌ 用户觉得不方便，不如群里直接表达 |
| 飞书消息历史 API 读群聊 | ⚠️ bot 需「获取群消息」权限，且飞书 bot 默认只能收到 @消息 | 待验证 |
| @对方 bot 传递上下文 | ✅ bot 间可通过 @触发 | ✅ 最自然，但需主动 @ |

**共享文件规范**（Plan B，已部署）：
- 路径：`~/.hermes/shared-memory.md`
- 格式：日期 + `[Agent名]` 标注来源
- 每次会话启动应读取，重要对话后追加

**消息历史 API**（Plan A 待探索）：
- 飞书 API: `GET /open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}`
- 需要 bot 有 `im:message:readonly` 权限，且 bot 在群内
- 实际能否拉到其他 bot 的消息取决于飞书权限策略

## 已知问题

- gateway 需要重启才能让新的 ALLOWED_USERS 生效
- 群发消息有时超时（可能是网络或 API 限流）
- openclaw 运行中但可能不在群里
- **Bot 间上下文不互通**：各自独立 memory，不知道对方聊过什么
