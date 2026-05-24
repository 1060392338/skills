---
name: opencli-browser-automation
description: 用 OpenCLI 替代 DrissionPage/CDP 进行浏览器自动化。支持 133+ 站点适配器 + 通用 browser 命令。ReAct 受控组件需原生注入。
category: chinese-platform-automation
---

# OpenCLI 浏览器自动化

## 安装

```bash
npm install -g @jackwener/opencli
```

### Chrome 扩展（必需）

OpenCLI 通过 Chrome 扩展与浏览器通信。扩展 manifest 含 `debugger` 权限，**必须手动加载**：

1. 下载扩展 zip：
   ```bash
   curl -sL "https://ghproxy.net/https://github.com/jackwener/OpenCLI/releases/download/v1.7.18/opencli-extension-v1.0.12.zip" -o /tmp/opencli-ext.zip
   mkdir -p ~/.opencli/extension && cd ~/.opencli/extension && unzip -o /tmp/opencli-ext.zip
   ```

2. Chrome → `chrome://extensions/` → 开「开发者模式」→「加载已解压的扩展程序」→ 选 `~/.opencli/extension/`

3. 验证：`opencli doctor`（应显示 `[OK] Extension: connected`）

⚠️ `--load-extension` CLI 参数**不生效**（因为 `debugger` 权限需手动授权）。

## 浏览器会话

```bash
# 打开 URL（自动创建会话）
opencli browser --session <name> --window foreground open "<url>"

# 读取页面状态（结构化元素列表，含 [N] 索引）
opencli browser --session <name> state

# 点击元素
opencli browser --session <name> click <N>

# 等待
opencli browser --session <name> wait time <seconds>
opencli browser --session <name> wait selector ".loaded"
```

## React 受控组件处理（关键坑）

`type` 命令对 React 受控组件报 `TypeError: Illegal invocation`。`fill`/`click` 也可能不触发 React 事件。

### 文本注入（必须 IIFE 包裹）

多次调用 `eval` 时变量会冲突。**必须用 IIFE 包裹**，否则报 `SyntaxError: Identifier 'el' has already been declared`：

```bash
opencli browser --session <name> eval "
(() => {
const el = document.querySelector('textarea[placeholder*=灵感]');
const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
ns.call(el, '你的文本');
el.dispatchEvent(new Event('input', {bubbles: true}));
el.dispatchEvent(new Event('change', {bubbles: true}));
return 'ok';
})()
"
```

### 按钮点击（React onClick）

```bash
opencli browser --session <name> eval "document.querySelector('[data-testid=create-song-button]').click()"
```

### 元素索引不稳定

`state` 返回的 `[N]` 索引在页面重载后会变化。不要硬编码索引，改用 `eval` + `data-testid` 选择器定位元素。

### Python 桥接层

`opencli_bridge.py`（位于 `~/.hermes/auto-douyinmusic/`）封装了 `subprocess` 调用。注意 `state` 输出的 stdout 第一行是 `URL:` 前缀，需跳过再 `json.loads()`。

## 抖音音乐平台适配

Douyin Music (`music.douyin.com/studio`) 是 React SPA：
- 导航用 `click` 元素索引（导航项 [10] AI作词, [12] AI作曲, [14] AI编辑器）
- 文本输入用 `eval` + 原生 setter（见上方）
- "生成歌曲"按钮用 `eval` + `.click()`
- 生成需等待 12+4s（素材列表刷新）
- 页面状态通过 `state` 命令读取，含 `data-testid` 属性便于定位

## 与 DrissionPage/CDP 对比

| 维度 | OpenCLI | DrissionPage |
|------|---------|-------------|
| 安装 | npm + 扩展 | pip |
| 页面读取 | `state` 结构化 JSON | `ele()`, `run_js()` |
| 交互 | `click`/`type`/`eval` | `click()`/`input()`/`run_js()` |
| React 支持 | 需 `eval` 原生注入 | 需原生 setter |
| 返回受限 | 无（eval 正常返回） | Chrome 147+ run_js 返回 None |
| 站点适配器 | 133+ 内置 | 无 |
| 浏览器管理 | daemon 进程 + 会话 | 手动管理端口 |

## 常用命令

```bash
opencli doctor                    # 诊断
opencli daemon status             # daemon 状态
opencli profile list              # Chrome profile 列表
opencli list                      # 列出所有 CLI 命令
opencli <site> --help             # 站点命令帮助
opencli browser --session dm close  # 关闭会话
```
