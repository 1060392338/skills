# TuriX-CUA OpenClaw Skill 集成指南

## 📦 已创建的文件结构

```
/Users/gallenwang/juan/project/workspace/skills/turix-cua/
├── SKILL.md                      # OpenClaw 技能定义（核心文件）
├── README.md                     # 详细使用指南
├── SETUP.md                      # 分步安装检查清单
├── INDEX.md                      # 包结构总览
├── scripts/
│   └── run_turix.sh             # 执行脚本（支持 UTF-8/中文）
└── examples/
    ├── ai-news-research.md      # 示例技能：AI 新闻调研
    └── github-repo-actions.md   # 示例技能：GitHub 操作
```

## 🚀 快速集成到 OpenClaw

### 方法 1：本地技能目录（推荐）

1. **复制技能到 OpenClaw 技能目录**
```bash
# 假设 OpenClaw 安装在默认位置
cp -r /Users/gallenwang/juan/project/workspace/skills/turix-cua \
      ~/.openclaw/skills/local/turix-cua/

# 或者如果使用 clawd
cp -r /Users/gallenwang/juan/project/workspace/skills/turix-cua \
      /path/to/clawd/skills/local/turix-cua/
```

2. **验证技能已加载**
```bash
# 在 OpenClaw 中查看可用技能
openclaw skills list
```

3. **在对话中使用**
```
用户：用 TuriX 打开 Safari 并访问 github.com
助手：好的，我来使用 TuriX-CUA 打开 Safari...
```

### 方法 2：使用 ClawHub 发布版本

访问：https://clawhub.ai/Tongyu-Yan/turix-cua

```bash
# 从 ClawHub 安装（如果支持）
openclaw skills install clawhub.ai/Tongyu-Yan/turix-cua
```

## ⚙️ 前置要求

### 1. 安装 TuriX-CUA
```bash
cd /Users/gallenwang/juan/project/workspace
git clone https://github.com/TurixAI/TuriX-CUA.git
cd TuriX-CUA
conda create -n turix_env python=3.12
conda activate turix_env
pip install -r requirements.txt
```

### 2. 配置 macOS 权限

**辅助功能权限：**
- 系统设置 → 隐私与安全 → 辅助功能
- 添加：Terminal、VSCode（或你的 IDE）

**Safari 自动化权限：**
- Safari → 设置 → 高级 → 显示开发菜单
- 开发 → 允许远程自动化
- 开发 → 允许来自 Apple 事件的 JavaScript

**触发权限对话框：**
```bash
osascript -e 'tell application "Safari" to do JavaScript "alert(\"Test\")" in document 1'
```

### 3. 配置 API 密钥

编辑 `TuriX-CUA/examples/config.json`：

**选项 A：TuriX API（推荐）**
- 获取密钥：https://turix.ai/api-platform/（$20 免费额度）
- 配置所有模型（brain、actor、memory、planner）

**选项 B：本地 Ollama**
```bash
ollama pull llama3.2-vision
```
配置为 ollama provider，base_url: http://localhost:11434

## 💡 使用示例

### 简单任务
```bash
# 打开应用
./skills/turix-cua/scripts/run_turix.sh "打开 Safari"

# 导航网页
./skills/turix-cua/scripts/run_turix.sh "打开 Chrome，访问 github.com"

# 系统操作
./skills/turix-cua/scripts/run_turix.sh "打开系统设置，启用深色模式"
```

### 复杂任务（启用规划）
```bash
# 多步骤任务
./skills/turix-cua/scripts/run_turix.sh \
  "在 GitHub 上搜索 TuriX-CUA，star 它，查看最新 issue" \
  --use-plan --use-skills

# 跨应用工作流
./skills/turix-cua/scripts/run_turix.sh \
  "打开 Discord，从老板消息下载 Excel，在 Numbers 创建图表，插入 PowerPoint，回复老板" \
  --use-plan
```

### 后台执行
```bash
# 后台运行，不阻塞终端
./skills/turix-cua/scripts/run_turix.sh "任务描述" --background

# 监控日志
tail -f TuriX-CUA/.turix_tmp/logging.log
```

### 恢复中断任务
```bash
# 恢复之前中断的任务
./skills/turix-cua/scripts/run_turix.sh --resume my-task-001
```

## 🔗 OpenClaw 集成模式

### 模式 1：纯 TuriX 任务
适合完全在 GUI 中完成的任务：
```
用户：帮我在 GitHub 上 star TuriX-CUA 项目
助手：好的，使用 TuriX-CUA 打开 GitHub 并搜索...
→ 调用 run_turix.sh
```

### 模式 2：OpenClaw + TuriX 混合
适合需要多种工具的任务：
```
用户：收集今日 AI 新闻并发送给 John

助手工作流：
1. web_fetch 抓取 36kr、虎嗅新闻（快速、可靠）
2. python-docx 创建 Word 文档（确定性）
3. run_turix.sh 发送文件给 John（GUI 操作）
```

### 模式 3：复杂自动化
适合多步骤、跨应用的任务：
```
用户：处理老板在 Discord 发的 Excel 文件

助手工作流：
1. run_turix.sh 打开 Discord，下载文件
2. python 处理 Excel 数据
3. run_turix.sh 在 Numbers 创建图表
4. run_turix.sh 插入 PowerPoint
5. run_turix.sh 回复老板
```

## 📊 监控与调试

### 检查状态
```bash
# 检查是否运行
ps aux | grep "python.*main.py" | grep -v grep

# 查看日志
tail -f TuriX-CUA/.turix_tmp/logging.log

# 查看步骤数
ls TuriX-CUA/.turix_tmp/brain_llm_interactions.log_brain_*.txt | wc -l
```

### 强制停止
```bash
# 快捷键：Cmd+Shift+2（在运行终端中）

# 命令行
pkill -f "python examples/main.py"
```

### 常见错误
| 错误 | 解决方案 |
|------|----------|
| `NoneType has no attribute 'save'` | 授予屏幕录制权限 |
| `Screen recording denied` | 系统设置 → 隐私 → 屏幕录制 → 添加 Terminal |
| `Conda environment not found` | `conda create -n turix_env python=3.12` |
| 模块导入错误 | `conda activate turix_env && pip install -r requirements.txt` |

## 🎯 最佳实践

### ✅ 推荐做法
1. **明确任务描述**
   - ✅ "打开 Safari，访问 google.com，搜索 AI 新闻"
   - ❌ "搜索一下"

2. **复杂任务启用规划**
   - 使用 `--use-plan` 处理多步骤任务
   - 使用 `--use-skills` 利用领域技能

3. **合理分工**
   - OpenClaw 负责：web_fetch、文件操作、数据处理
   - TuriX 负责：GUI 导航、应用操作、文件发送

4. **监控长任务**
   - 使用 `--background` 后台执行
   - 实时监控日志：`tail -f .turix_tmp/logging.log`

5. **创建领域技能**
   - 为重复任务创建 TuriX skill（markdown 文件）
   - 放在 `TuriX-CUA/skills/` 目录

### ❌ 避免做法
1. 模糊指令："帮我弄一下"
2. 提及坐标：TuriX 使用视觉理解，不需要坐标
3. 系统级操作：无需权限的情况下不要尝试
4. 期望 100% 成功率：这是 AI，不是确定性程序

## 📚 文档导航

| 文档 | 用途 | 目标读者 |
|------|------|----------|
| `SKILL.md` | OpenClaw 技能定义 | OpenClaw（自动读取） |
| `README.md` | 详细使用指南 | 最终用户 |
| `SETUP.md` | 安装检查清单 | 初次安装者 |
| `INDEX.md` | 包结构总览 | 开发者/高级用户 |
| `examples/*.md` | TuriX 技能示例 | 技能开发者 |

## 🔄 更新与维护

### 检查更新
```bash
# 查看 TuriX-CUA 更新
cd TuriX-CUA
git pull

# 查看技能包更新
cd /Users/gallenwang/juan/project/workspace/skills/turix-cua
git status
```

### 贡献技能
1. 在 `examples/` 创建新的技能 markdown 文件
2. 遵循 YAML frontmatter 格式
3. 提供清晰的工作流程指导
4. 提交到 GitHub 或 ClawHub

## 📞 获取帮助

1. **文档**
   - 查看 `SETUP.md` 安装检查清单
   - 查看 `README.md` 使用示例
   - 查看 `SKILL.md` 技能定义

2. **日志**
   ```bash
   tail -f TuriX-CUA/.turix_tmp/logging.log
   ```

3. **社区**
   - Discord: https://discord.gg/yaYrNAckb5
   - GitHub Issues: https://github.com/TurixAI/TuriX-CUA/issues

4. **联系方式**
   - Email: contact@turix.ai
   - 网站：https://turix.ai

## 🎉 完成！

现在你已经成功集成了 TuriX-CUA skill 到 OpenClaw！

**下一步：**
1. 完成 `SETUP.md` 中的所有检查项
2. 运行测试任务验证安装
3. 开始使用 TuriX 自动化你的桌面工作流

---

**创建日期**: 2026-02-23  
**版本**: 1.0.0  
**兼容性**: OpenClaw + TuriX-CUA v0.3+  
**平台**: macOS 15+
