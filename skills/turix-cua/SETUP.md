# TuriX-CUA Setup Checklist

## ✅ Pre-Installation

- [ ] macOS 15 or later
- [ ] Conda installed (version ≥ 22.9)
- [ ] Git installed
- [ ] Safari installed (required for automation)

## 📦 Installation Steps

### 1. Clone TuriX-CUA Repository
```bash
cd /Users/gallenwang/juan/project/workspace
git clone https://github.com/TurixAI/TuriX-CUA.git
```
- [ ] Completed

### 2. Create Python Environment
```bash
cd TuriX-CUA
conda create -n turix_env python=3.12
conda activate turix_env
pip install -r requirements.txt
```
- [ ] Environment created
- [ ] Dependencies installed

### 3. Grant Accessibility Permission
1. Open **System Settings → Privacy & Security → Accessibility**
2. Click **+** button
3. Add **Terminal**
4. Add **VSCode** (or your IDE)
5. Add **/usr/bin/python3** (if issues persist)

- [ ] Terminal added
- [ ] IDE added
- [ ] python3 added (if needed)

### 4. Configure Safari Automation
1. Open **Safari**
2. Go to **Safari → Settings → Advanced**
3. Check **Show features for web developers**
4. In menu bar, click **Develop**
5. Check **Allow Remote Automation**
6. Check **Allow JavaScript from Apple Events**

- [ ] Developer features enabled
- [ ] Remote Automation enabled
- [ ] JavaScript from Apple Events enabled

### 5. Trigger Permission Dialogs
Run in Terminal:
```bash
osascript -e 'tell application "Safari" to do JavaScript "alert(\"Triggering accessibility request\")" in document 1'
```
- [ ] Click **Allow** on the Safari dialog
- [ ] Repeat in VSCode integrated terminal if using VSCode

### 6. Configure API Keys

**Option A: TuriX API (Recommended)**
1. Visit https://turix.ai/api-platform/
2. Sign up / Login
3. Copy API key
4. Edit `TuriX-CUA/examples/config.json`:
   ```json
   {
     "brain_llm": { "api_key": "YOUR_KEY_HERE" },
     "actor_llm": { "api_key": "YOUR_KEY_HERE" },
     "memory_llm": { "api_key": "YOUR_KEY_HERE" },
     "planner_llm": { "api_key": "YOUR_KEY_HERE" }
   }
   ```

**Option B: Local Ollama**
1. Install Ollama: https://ollama.ai
2. Run: `ollama pull llama3.2-vision`
3. Update config.json to use ollama provider

- [ ] API keys configured
- [ ] Config file saved

### 7. Test Installation
```bash
cd /Users/gallenwang/juan/project/workspace
./skills/turix-cua/scripts/run_turix.sh "Open Safari"
```
- [ ] TuriX starts successfully
- [ ] Safari opens
- [ ] No errors in logs

## 🧪 Verification Tests

### Test 1: Basic Navigation
```bash
./skills/turix-cua/scripts/run_turix.sh "Open Safari, go to google.com"
```
- [ ] Safari opens
- [ ] Navigates to google.com

### Test 2: System Settings
```bash
./skills/turix-cua/scripts/run_turix.sh "Open System Settings"
```
- [ ] System Settings opens

### Test 3: Complex Task (with planning)
```bash
./skills/turix-cua/scripts/run_turix.sh "Search AI news on google" --use-plan
```
- [ ] Planner activates
- [ ] Search executes
- [ ] Results found

## 📊 Performance Check

- [ ] First run model loading: 2-5 minutes (normal)
- [ ] Subsequent runs: < 30 seconds
- [ ] Logs created in `.turix_tmp/`
- [ ] Screenshots captured each step

## 🔧 Troubleshooting

### Common Issues

**Issue**: `Conda environment not found`
- **Fix**: `conda create -n turix_env python=3.12`

**Issue**: `ModuleNotFoundError`
- **Fix**: 
  ```bash
  conda activate turix_env
  pip install -r requirements.txt
  ```

**Issue**: `Screen recording access denied`
- **Fix**: 
  1. System Settings → Privacy → Screen Recording → Add Terminal
  2. Restart Terminal
  3. Run Safari trigger again

**Issue**: `NoneType has no attribute 'save'`
- **Fix**: Grant Screen Recording permission (see above)

**Issue**: Task stuck on step 1
- **Fix**: Check if `.turix_tmp/` directory exists
- **Fix**: Check logs: `tail -f TuriX-CUA/.turix_tmp/logging.log`

## 📝 Configuration Reference

### config.json Structure
```json
{
  "agent": {
    "task": "Your task description",
    "use_plan": false,
    "use_skills": false,
    "resume": false,
    "agent_id": "auto-generated",
    "max_steps": 100,
    "max_actions_per_step": 5
  },
  "brain_llm": {
    "provider": "turix",
    "model_name": "turix-brain-model",
    "api_key": "YOUR_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "turix-actor-model",
    "api_key": "YOUR_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "memory_llm": {
    "provider": "turix",
    "model_name": "turix-memory-model",
    "api_key": "YOUR_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  },
  "planner_llm": {
    "provider": "turix",
    "model_name": "turix-planner-model",
    "api_key": "YOUR_KEY",
    "base_url": "https://llm.turixapi.io/v1"
  }
}
```

## 🎯 Ready to Use!

Once all checkboxes are complete, you're ready to use TuriX-CUA with OpenClaw!

### Quick Start Commands
```bash
# Simple task
./skills/turix-cua/scripts/run_turix.sh "Open Chrome"

# Complex task
./skills/turix-cua/scripts/run_turix.sh "Search and summarize news" --use-plan

# Background execution
./skills/turix-cua/scripts/run_turix.sh "Task" --background

# Monitor
tail -f TuriX-CUA/.turix_tmp/logging.log
```

## 📚 Next Steps

1. Read `SKILL.md` for detailed usage guide
2. Read `README.md` for examples and best practices
3. Join Discord: https://discord.gg/yaYrNAckb5
4. Check ClawHub: https://clawhub.ai/Tongyu-Yan/turix-cua

---

**Setup Date**: _______________  
**Setup By**: _______________  
**Notes**: _______________
