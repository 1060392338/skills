---
name: feishu-bot-creation-guide
description: Step-by-step guide for manually creating a Feishu bot via open.feishu.cn when browser access fails
category: devops
version: 1.0.0
metadata:
  hermes:
    tags: [feishu, bot, manual]
    related_skills: [hermes-feishu-setup, feishu-bot-debug]
---

# Feishu Bot Creation Guide

## When Browser Fails

If `open.feishu.cn` times out in browser (common issue), do NOT keep retrying. Instead provide these manual steps to the user.

## Step-by-Step: Create a Feishu Bot

### 1. Create App
- URL: https://open.feishu.cn/app
- Click 「创建企业自建应用」
- Fill in:
  - App name: (user-provided name)
  - Description: Hermes Agent Feishu bot
  - Icon: (optional)

### 2. Get Credentials
After creation, go to 「凭证与基础信息」 page:
- **App ID**: `cli_xxxxxxxx`
- **App Secret**: (click to reveal)

### 3. Enable Bot Capability
- Go to 「应用功能」→「机器人」
- Click 「开启」
- Configure:
  - Bot name
  - Bot description

### 4. Configure Permissions
- Go to 「权限管理」
- Enable:
  - `im:message` (send messages)
  - `im:message.receive_v1` (receive messages)
  - `im:chat` (group chat management)

### 5. Publish
- Go to 「版本管理与发布」
- Create version and submit
- Click 「发布」

### 6. Get Bot Open ID (after publishing)
After setup, the bot needs its `open_id` for configuration. Can be obtained via:
```bash
curl "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "CLI_xxx", "app_secret": "xxx"}'
```

## After User Provides Credentials
Use `hermes-feishu-setup` skill to configure the bot in Hermes Gateway.

## Alternative: Use Local Chrome + Puppeteer

If cloud browser is blocked by Feishu, use local Chrome with puppeteer-core:
```bash
cd /tmp && mkdir -p puppeteer_test && cd puppeteer_test
npm init -y && npm install puppeteer-core
```

Script: `/tmp/puppeteer_test/feishu_create.js` (uses local `/Applications/Google Chrome.app`)

⚠️ Note: Requires user to be logged in. If redirected to login page, user must either:
1. Provide Chrome cookies/session
2. Manually create (faster in practice)

## Verification After User Says "Done"

User may say bot is created but bot capability not enabled. Always verify:
```bash
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id": "CLI_xxx", "app_secret": "xxx"}' | jq -r '.tenant_access_token')
curl -s 'https://open.feishu.cn/open-apis/bot/v3/info' -H "Authorization: Bearer $TOKEN"
# 成功: {"code":0, "bot":{...}}
# 未启用bot能力: {"code":11205, "msg":"app do not have bot"}
```

## Known Limitation
- `open.feishu.cn` frequently times out in browser tool (cloud IPs blocked)
- Manual creation is the reliable workaround
