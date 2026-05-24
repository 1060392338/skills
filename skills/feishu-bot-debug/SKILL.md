---
name: feishu-bot-debug
category: devops
description: Debug Feishu bot communication issues — get bot open_ids, fix allowlist, diagnose bot-to-bot message visibility
---

# Feishu Bot Debug & Cross-Bot Communication Setup

## Context
When multiple Feishu bots need to see each other's messages in a group, the `FEISHU_ALLOWED_USERS` in `.env` must include ALL bots' open_ids, not just the user's. Bots not in the allowlist will have their messages silently dropped.

## How to Get Bot Open IDs

### Step 1: Authenticate with tenant_access_token
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
```

### Step 2: Get bot info (includes open_id)
```bash
curl -s -X GET "https://open.feishu.cn/open-apis/bot/v3/info" \
  -H "Authorization: Bearer <tenant_access_token>"
```

Response: `{"bot":{"open_id":"ou_xxxxx","app_name":"xxx",...}}`

### Step 3: Update FEISHU_ALLOWED_USERS in .env
Format is comma-separated open_ids:
```
FEISHU_ALLOWED_USERS=ou_<user>,ou_<bot1>,ou_<bot2>,ou_<bot3>
```

## Common Issues
- `code:10014, msg:"app secret invalid"` → App Secret is wrong, try different versions
- Bots only receive messages that @ them (Feishu platform limitation)
- Bot-to-bot without @mention: other bots CANNOT see it (Feishu design)
- Bot-to-bot WITH @mention: works if sender is in allowlist

## Bot Open IDs (2026-04-24, verified)
| Bot | AppID | Open ID |
|-----|-------|---------|
| openclaw | cli_a927388202b89cc8 | ou_cd468a4ab7bc50207d50612e7c189e83 |
| mac | cli_a956d74d8b389bc2 | ou_73bb5a7d5c14fbf5b2d2df1610be2b37 |
| Hermes | cli_a960a49baef99bdd | ou_8a17e9f2b804647a9d9af73ae0f6d9c0 |
| machermes | cli_a956d74d8b389bc2 | (same app as mac? needs re-check) |
