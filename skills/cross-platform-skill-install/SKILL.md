---
name: cross-platform-skill-install
description: 安装带 SKILL.md 的 GitHub 工具并注册到 Hermes / OpenClaw / Claude Code 三平台。含国内网络下的 GitHub 下载技巧。
---

# 跨平台 Skill 安装

将 GitHub 上的工具（带 SKILL.md）安装并注册到三平台：Hermes、OpenClaw、Claude Code。

## 触发条件
- 用户要求安装某个 GitHub 工具（如 browser-harness）
- 需要让新工具在所有三个 Agent 平台可用

## 三平台 Skill 机制速查

| 平台 | 方式 | 示例 |
|------|------|------|
| **Claude Code** | `@` 引用 | `~/.claude/CLAUDE.md` 中加 `@~/Developer/<tool>/SKILL.md` |
| **Hermes** | Skill 目录拷贝 | `~/.hermes/skills/<name>/SKILL.md` |
| **OpenClaw** | Skill 目录拷贝 | `~/.openclaw/skills/<name>/SKILL.md` |
| **~/.agents** | 共享源 | `~/.agents/skills/<name>/SKILL.md`（CC symlink 指向这里） |

## 安装步骤

### 1. 下载（国内网络）

优先用 codeload zip，git clone 和 ghproxy 经常超时：

```bash
# codeload zip（最可靠）
curl -sL --connect-timeout 15 --max-time 120 \
  -o /tmp/repo.zip \
  "https://codeload.github.com/<owner>/<repo>/zip/refs/heads/main"
mkdir -p ~/Developer/<repo>
unzip -qo /tmp/repo.zip -d /tmp/
cp -r /tmp/<repo>-main/* ~/Developer/<repo>/
```

### 2. 安装工具

```bash
cd ~/Developer/<repo>
uv tool install -e .
```

### 3. 注册到三平台

```bash
REPO=~/Developer/<tool-name>

# Claude Code
echo "@$REPO/SKILL.md" >> ~/.claude/CLAUDE.md

# Hermes
mkdir -p ~/.hermes/skills/<tool-name>
cp $REPO/SKILL.md ~/.hermes/skills/<tool-name>/SKILL.md

# OpenClaw
mkdir -p ~/.openclaw/skills/<tool-name>
cp $REPO/SKILL.md ~/.openclaw/skills/<tool-name>/SKILL.md

# ~/.agents 共享源
mkdir -p ~/.agents/skills/<tool-name>
cp $REPO/SKILL.md ~/.agents/skills/<tool-name>/SKILL.md
```

### 4. 验证

```bash
command -v <tool-name> && <tool-name> --version
ls ~/.hermes/skills/<tool-name>/SKILL.md
ls ~/.openclaw/skills/<tool-name>/SKILL.md
ls ~/.agents/skills/<tool-name>/SKILL.md
```

## 平台间 Skill 共享架构

```
~/.agents/skills/          <- 共享源（核心 + 用户安装）
    ├─ symlink -> ~/.claude/skills/    CC
    └─ copy    -> ~/.openclaw/skills/  OC

~/.hermes/skills/           <- 独立目录，需手动同步
```

## 已安装的工具

| 工具 | 路径 | 用途 |
|------|------|------|
| browser-harness | ~/Developer/browser-harness | CDP 直连 Chrome |
