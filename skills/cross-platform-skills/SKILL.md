---
name: cross-platform-skills
description: Hermes + OpenClaw + Claude Code 三平台 skill 共享架构 — 统一管理、分类同步、GitHub 托管
---

# 跨平台 Skill 共享架构

## 触发条件
- 新增/修改 skill 需要三平台同步
- 从 Hermes 导出 skill 到其他平台
- 初始化或重建共享 skill 仓库

## 架构

```
~/.agents/skills/          <- 共享源（Git 仓库，推 GitHub）
    |-- symlink -> ~/.claude/skills/        Claude Code（自动同步）
    |-- 拷贝    -> ~/.openclaw/skills/      OpenClaw（手动同步）
    |-- tap     -> ~/.hermes/skills/        Hermes（hermes skills tap add）
```

OpenClaw 禁止 symlink 指向 ~/.openclaw/ 外部，只能用拷贝。

## Skill 分类策略

Tier 1 强烈推荐共享：chinese-code-review, chinese-commit-conventions, chinese-documentation, chinese-git-workflow, karpathy-coding-principles, clawcode-driven-development, project-knowledge-strategy, mcp-builder

Tier 2 建议共享：feishu-bot-debug, feishu-bypass-terminal, feishu-image-upload, feishu-bot-creation-guide, feishu-multi-bot-debug, opencli-browser-automation

Tier 3 可选：fix-npm-global-bin, github-repo-upload, webui-launcher, workflow-runner, bypass-terminal-masking, webhook-subscriptions, dogfood, three-layer-memory-architecture

不推荐：项目特定(toutiao-*, douyin-*)、平台绑定(hermes-*, openclaw-*)、领域窄(mlops/*, gaming/*, creative/*)

## 同步步骤

1. Hermes 导出到共享源：
   Hermes skill 可能在子目录(software-development/, devops/, chinese-platform-automation/)
   用 find 定位后 cp -r 到 ~/.agents/skills/

2. 同步到 OpenClaw：
   cp -r ~/.agents/skills/<name> ~/.openclaw/skills/<name>

3. Claude Code 已通过 symlink 自动同步

4. GitHub 推送 + Hermes tap（GitHub 仓库建好后执行）

## 当前状态

~/.agents/skills/: 34 skills
CC symlink: 自动同步
OC: 手动拷贝同步
Hermes: 59+ skills，待 tap 后整合

## 网络注意
- gh CLI 安装：brew install gh 可能被锁，可尝试直接下载二进制
- 小文件用 codeload.github.com 直连比 ghproxy 快
