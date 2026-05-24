# TuriX-CUA Skill for OpenClaw

🤖 **Desktop Actions, Driven by AI**

This skill package enables OpenClaw to control macOS desktop visually using the TuriX Computer Use Agent (CUA).

## 📦 What's Included

```
skills/turix-cua/
├── SKILL.md              # OpenClaw skill documentation
├── README.md             # This file - detailed setup guide
├── scripts/
│   └── run_turix.sh      # Execution script
└── SETUP.md              # Quick setup checklist
```

## 🚀 Quick Setup

### Step 1: Clone TuriX-CUA

```bash
cd /Users/gallenwang/juan/project/workspace
git clone https://github.com/TurixAI/TuriX-CUA.git
```

### Step 2: Install Dependencies

```bash
cd TuriX-CUA
conda create -n turix_env python=3.12
conda activate turix_env
pip install -r requirements.txt
```

### Step 3: Grant macOS Permissions

#### 3.1 Accessibility
1. Open **System Settings → Privacy & Security → Accessibility**
2. Click **+**, add **Terminal** and **VSCode** (or your IDE)
3. If issues persist, also add **/usr/bin/python3**

#### 3.2 Safari Automation
1. **Safari → Settings → Advanced** → Enable **Show features for web developers**
2. In new **Develop** menu, enable:
   - **Allow Remote Automation**
   - **Allow JavaScript from Apple Events**

#### 3.3 Trigger Permission Dialogs
Run once in each terminal you'll use:
```bash
osascript -e 'tell application "Safari" to do JavaScript "alert(\"Triggering accessibility request\")" in document 1'
```
Click **Allow** on the dialog.

### Step 4: Configure API Keys

Edit `TuriX-CUA/examples/config.json`:

**Option A: TuriX API (Recommended)**
Get API key from https://turix.ai/api-platform/ ($20 free credit)

```json
{
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "turix-actor-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "memory_llm": {
    "provider": "turix",
    "model_name": "turix-memory-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "planner_llm": {
    "provider": "turix",
    "model_name": "turix-planner-model",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  }
}
```

**Option B: Local Ollama**
```bash
ollama pull llama3.2-vision
```

```json
{
  "brain_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  }
  // ... same for actor, memory, planner
}
```

### Step 5: Test Installation

```bash
cd /Users/gallenwang/juan/project/workspace
./skills/turix-cua/scripts/run_turix.sh "Open Safari"
```

## 📖 Usage

### Basic Commands

```bash
# Simple task
./skills/turix-cua/scripts/run_turix.sh "Open Chrome and go to github.com"

# Complex task with planning
./skills/turix-cua/scripts/run_turix.sh "Search AI news and create summary" --use-plan --use-skills

# Run in background
./skills/turix-cua/scripts/run_turix.sh "Task" --background

# Resume interrupted task
./skills/turix-cua/scripts/run_turix.sh --resume my-task-001

# Check status
./skills/turix-cua/scripts/run_turix.sh
```

### Command Options

| Option | Description |
|--------|-------------|
| `--use-plan` | Enable planning for complex tasks |
| `--use-skills` | Enable skill selection |
| `--agent-id <id>` | Set custom agent ID |
| `--resume` | Resume interrupted task |
| `--background` | Run in background (non-blocking) |
| `--help` | Show help message |

## 🎯 Task Examples

### ✅ Good Tasks

**Simple:**
- "Open Safari, go to google.com, search for 'TuriX AI'"
- "Open System Settings, enable Dark Mode"
- "Open Finder, navigate to Documents, create folder 'Projects'"

**Complex (use `--use-plan`):**
- "Search iPhone 17 price on Apple store, create Pages document, send to contact John"
- "Open Discord, find Excel file from boss, create chart in Numbers, insert to PowerPoint"
- "Search AI news on 36kr and Huxiu, summarize top 5 stories, save to Word"

### ❌ Avoid

- Vague: "Help me" / "Fix this"
- Impossible: "Delete all files"
- No context: "Do it"
- System-level: "Install software"

## 📊 Monitoring

### Check Status
```bash
# Check if running
ps aux | grep "python.*main.py" | grep -v grep

# View logs in real-time
tail -f TuriX-CUA/.turix_tmp/logging.log

# List step files
ls -lt TuriX-CUA/examples/.turix_tmp/brain_llm_interactions.log_brain_*.txt
```

### Force Stop

**Hotkey**: `Cmd+Shift+2` (in running terminal)

**Command**:
```bash
pkill -f "python examples/main.py"
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `NoneType has no attribute 'save'` | Grant Screen Recording permission |
| `Screen recording denied` | Run Safari trigger, click Allow |
| `Conda environment not found` | `conda create -n turix_env python=3.12` |
| Module errors | `conda activate turix_env && pip install -r requirements.txt` |
| Keyboard errors | Add Terminal to Accessibility |
| Task stuck | Check `.turix_tmp/` exists |

## 📚 Resources

- **TuriX GitHub**: https://github.com/TurixAI/TuriX-CUA
- **ClawHub**: https://clawhub.ai/Tongyu-Yan/turix-cua
- **Discord**: https://discord.gg/yaYrNAckb5
- **Website**: https://turix.ai
- **API**: https://turixapi.io

## 📝 Notes

- **First run**: 2-5 minutes to load AI models
- **Subsequent runs**: Much faster (models cached)
- **Chinese text**: Fully supported via UTF-8 handling
- **Platform**: macOS 15+ only (Windows support in separate branch)

## 🤝 Contributing

Found issues or have suggestions? Please open an issue on:
- TuriX-CUA: https://github.com/TurixAI/TuriX-CUA/issues
- This skill: Contact the skill creator

---

**Version**: 1.0.0  
**Created**: 2026-02-23  
**Compatibility**: OpenClaw + TuriX-CUA v0.3+
