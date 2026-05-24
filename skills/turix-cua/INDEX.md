# TuriX-CUA Skill Package Index

📦 **OpenClaw Skill Package for TuriX Computer Use Agent**

## 📁 Package Structure

```
skills/turix-cua/
├── INDEX.md                  # This file - package overview
├── SKILL.md                  # Main OpenClaw skill definition
├── README.md                 # Detailed user guide
├── SETUP.md                  # Step-by-step setup checklist
├── scripts/
│   └── run_turix.sh          # Main execution script
└── examples/
    ├── ai-news-research.md   # Example skill: AI news gathering
    └── github-repo-actions.md # Example skill: GitHub operations
```

## 🎯 Quick Reference

### For OpenClaw Users

**Enable this skill in OpenClaw:**
```bash
# Copy skill to OpenClaw skills directory
cp -r /Users/gallenwang/juan/project/workspace/skills/turix-cua \
      /path/to/clawd/skills/local/turix-cua/
```

**Use in conversation:**
- "用 TuriX 打开 Safari 并访问 github.com"
- "在 GitHub 上搜索 TuriX-CUA 并 star 它"
- "搜索 AI 新闻并生成摘要"

### For Skill Developers

**Key Files:**
- `SKILL.md` - OpenClaw skill definition (YAML frontmatter + instructions)
- `scripts/run_turix.sh` - Execution wrapper with UTF-8 support
- `examples/*.md` - TuriX skill templates for specific domains

## 🚀 Core Features

### 1. Multi-Model Architecture
- **Brain**: Task understanding and reasoning
- **Actor**: Precise UI action execution
- **Planner**: High-level task decomposition
- **Memory**: Context maintenance across steps

### 2. Skills System
- Markdown playbooks for specific domains
- Planner selects based on name + description
- Brain uses full content for execution guidance

### 3. Resume Capability
- Interrupted tasks can be resumed
- Stable `agent_id` for task tracking
- Memory persisted to disk

### 4. UTF-8 Support
- Proper Chinese text handling
- Python-based config updates
- No shell interpolation issues

## 📋 Usage Patterns

### Pattern 1: Direct Desktop Control
```bash
# OpenClaw → TuriX Skill → run_turix.sh → TuriX Agent → macOS UI
./run_turix.sh "Open Chrome, go to google.com, search 'AI news'"
```

### Pattern 2: Information Gathering + Document Creation
```python
# 1. OpenClaw fetches info (fast, reliable)
news = web_fetch("https://36kr.com")

# 2. OpenClaw creates document (fast, deterministic)
doc = create_word_doc(news)

# 3. TuriX sends file (GUI task)
./run_turix.sh "Send document.docx to contact John via Messages"
```

### Pattern 3: Complex Multi-Step Workflow
```bash
# Enable planning for complex tasks
./run_turix.sh "Search AI news, summarize, create doc, send to boss" \
  --use-plan --use-skills
```

## 🔧 Configuration Quick Reference

### Basic Config (examples/config.json)
```json
{
  "agent": {
    "task": "Your task here",
    "use_plan": false,
    "use_skills": false,
    "resume": false,
    "max_steps": 100
  },
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain-model",
    "api_key": "YOUR_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  }
  // ... actor, memory, planner
}
```

### Script Options
```bash
./run_turix.sh "Task" [OPTIONS]

OPTIONS:
  --use-plan      Enable planning
  --use-skills    Enable skill selection
  --agent-id ID   Set custom agent ID
  --resume        Resume interrupted task
  --background    Run in background
  --help          Show help
```

## 📊 Monitoring Commands

```bash
# Check if running
ps aux | grep "python.*main.py" | grep -v grep

# View logs
tail -f TuriX-CUA/.turix_tmp/logging.log

# List steps completed
ls TuriX-CUA/.turix_tmp/brain_llm_interactions.log_brain_*.txt | wc -l

# Force stop
pkill -f "python examples/main.py"

# Hotkey: Cmd+Shift+2
```

## 🎓 Learning Path

### Beginner
1. ✅ Complete `SETUP.md` checklist
2. ✅ Run simple test: "Open Safari"
3. ✅ Read `README.md` for examples
4. ✅ Try basic tasks (open app, navigate)

### Intermediate
1. ✅ Use `--use-plan` for complex tasks
2. ✅ Create custom TuriX skills in `examples/`
3. ✅ Monitor and debug using logs
4. ✅ Integrate with OpenClaw workflows

### Advanced
1. ✅ Customize TuriX models in `config.json`
2. ✅ Use Ollama for local inference
3. ✅ Implement resume for long tasks
4. ✅ Build domain-specific skills

## 🔗 External Resources

| Resource | URL |
|----------|-----|
| TuriX GitHub | https://github.com/TurixAI/TuriX-CUA |
| ClawHub Skill | https://clawhub.ai/Tongyu-Yan/turix-cua |
| Discord Community | https://discord.gg/yaYrNAckb5 |
| TuriX Website | https://turix.ai |
| API Platform | https://turixapi.io |
| Technical Report | https://turix.ai/technical-report/ |

## 🐛 Troubleshooting Quick Guide

| Problem | Quick Fix |
|---------|-----------|
| Permission denied | System Settings → Privacy → Accessibility → Add Terminal |
| Screen recording denied | Add Terminal to Screen Recording, restart Terminal |
| Conda not found | `conda create -n turix_env python=3.12` |
| Module errors | `conda activate turix_env && pip install -r requirements.txt` |
| Task stuck | Check logs: `tail -f .turix_tmp/logging.log` |
| Models slow | First run is slow (2-5 min), subsequent runs faster |

## 📝 Example Workflows

### Workflow 1: Daily AI News Briefing
```bash
# 1. Gather news (OpenClaw web_fetch - fast)
# 2. Create Word doc (OpenClaw python-docx - reliable)
# 3. Send via Messages (TuriX - GUI task)
./run_turix.sh "Send AI_News_Briefing.docx to contact John via Messages"
```

### Workflow 2: GitHub Project Research
```bash
# Use TuriX skill for GitHub operations
./run_turix.sh "Search TuriX-CUA on GitHub, star it, check latest issues" \
  --use-skills
```

### Workflow 3: Cross-App Data Transfer
```bash
# Complex multi-app workflow
./run_turix.sh "Open Discord, download Excel from boss, \
  create chart in Numbers, insert to PowerPoint, reply to boss" \
  --use-plan
```

## 🎯 Best Practices

### ✅ DO
- Be specific in task descriptions
- Use `--use-plan` for complex multi-step tasks
- Monitor progress via logs
- Use resume for long-running tasks
- Create custom skills for repeated workflows
- Combine OpenClaw tools (web_fetch, exec) with TuriX

### ❌ DON'T
- Use vague instructions ("Help me", "Do it")
- Mention exact coordinates (TuriX uses visual understanding)
- Run system-level operations without permission
- Expect 100% success rate (it's AI, not deterministic)
- Use for tasks better suited to CLI/API

## 📈 Performance Expectations

| Metric | Value |
|--------|-------|
| First run (model load) | 2-5 minutes |
| Subsequent runs | < 30 seconds |
| Simple task steps | 3-8 steps |
| Complex task steps | 15-30 steps |
| Success rate (internal) | > 68% (OSWorld-style) |
| Max recommended steps | 100 |

## 🆘 Getting Help

1. **Check Documentation**
   - `SKILL.md` - OpenClaw integration
   - `README.md` - Usage guide
   - `SETUP.md` - Installation checklist

2. **Check Logs**
   ```bash
   tail -f TuriX-CUA/.turix_tmp/logging.log
   ```

3. **Community Support**
   - Discord: https://discord.gg/yaYrNAckb5
   - GitHub Issues: https://github.com/TurixAI/TuriX-CUA/issues

4. **Contact**
   - Email: contact@turix.ai

---

**Package Version**: 1.0.0  
**Created**: 2026-02-23  
**Maintainer**: OpenClaw Community  
**License**: Follow TuriX-CUA license
