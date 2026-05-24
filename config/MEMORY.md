# MEMORY.md — 全局记忆（跨平台通用版）

## 项目摘要

- **框架**: OpenClaw
- **频道**: 飞书 + 微信
- **核心工作流**: 虾皮跨境电商自动化（shopee-auto-workflow）
- **Skills 策略**: 按需启用

## Agent 工作规范

见 AGENTS.md（ClawCode 驱动的工作流规范）

## 核心原则

1. 大任务分批输出，不等全部完成
2. 超过 10 分钟无输出 → 停止，告知进度和卡点
3. 破坏性操作先问，trash > rm
4. 上下文 >60% 立即停手，结论写文件
5. 任务完成后强制调用 save_session()

## 环境配置指引（新电脑适配）

- `openclaw.json` 需配置：
  - models.providers: 根据新电脑可用的 API 配置
  - channels.feishu: 飞书 appId / appSecret / domain / connectionMode
  - channels.openclaw-weixin: 微信插件（需重新扫码登录）
  - plugins.allow: feishu, openclaw-weixin, memory-core, deepseek
- 微信登录：`openclaw channels login --channel openclaw-weixin`
- Skills：按需启用，推荐 find-skills / qrcode-skills / self-improving-agent

## 跨平台注意事项

- openclaw.json 含 API Key，不要直接上传
- 微信登录凭证需在新电脑重新扫码
- 模型 provider 需根据新机器环境调整
