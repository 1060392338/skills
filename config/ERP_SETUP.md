# 璺ㄥ鐢靛晢ERP宸ヤ綔娴?鈥?鏂扮數鑴戦厤缃寚寮?
## 鐩綍

1. [鐜鍑嗗](#1-鐜鍑嗗)
2. [椤圭洰浠ｇ爜](#2-椤圭洰浠ｇ爜)
3. [閰嶇疆鏂囦欢](#3-閰嶇疆鏂囦欢)
4. [娴忚鍣ㄨ缃甝(#4-娴忚鍣ㄨ缃?
5. [搴楅摵鏄犲皠琛╙(#5-搴楅摵鏄犲皠琛?
6. [杩愯](#6-杩愯)

---

## 1. 鐜鍑嗗

### 瀹夎 Python

鎺ㄨ崘 Python 3.12锛岀郴缁熺幆澧冨嵆鍙紝涓嶈铏氭嫙鐜銆?
```
python --version
```

濡傛灉娌¤锛屽幓 https://www.python.org/downloads/ 涓嬭浇 3.12 骞跺畨瑁咃紙瀹夎鏃跺嬀閫?Add to PATH"锛夈€?
### 瀹夎 Node.js

```
node --version
npm --version
```

闇€瑕?Node.js 18+銆傚幓 https://nodejs.org/ 涓嬭浇瀹夎銆?
### 瀹夎 OpenClaw

```
npm install -g openclaw
openclaw setup
```

鎸夋彁绀哄畬鎴愬熀鏈垵濮嬪寲銆?
---

## 2. 椤圭洰浠ｇ爜

鐢靛晢宸ヤ綔娴佺殑浠ｇ爜鍦ㄦ湰鏈猴紝涓嶅湪 GitHub 浠撳簱閲屻€?
### 鏂规A锛氫粠鏃х數鑴戞嫹璐?
鎶?`cross-border-erp-agent-new` 鏁翠釜鐩綍澶嶅埗鍒版柊鐢佃剳鐨?OpenClaw workspace 涓嬶細

```
~/.openclaw/workspace/cross-border-erp-agent-new/
```

### 鏂规B锛氶噸鏂版惌寤猴紙濡傛灉浣犺寰楃洰褰曞悕锛?
鍦?workspace 涓嬪垱寤?`cross-border-erp-agent-new` 鐩綍锛屾妸鎵€鏈夌殑 .py 鏂囦欢澶嶅埗杩涘幓銆?
### 瀹夎 Python 渚濊禆

```
cd ~/.openclaw/workspace/cross-border-erp-agent-new
pip install playwright dotenv openai httpx
playwright install chromium
```

---

## 3. 閰嶇疆鏂囦欢

椤圭洰浠ｇ爜寮曠敤浜嗗嚑涓閮ㄩ厤缃紝浣犻渶瑕佹墜鍔ㄥ垱寤恒€?
### 3.1 .env 鏂囦欢

鍦ㄩ」鐩洰褰曚笅鍒涘缓 `.env`锛?
```
# LLM API 閰嶇疆
LLM_API_KEY=浣犵殑API_KEY
LLM_BASE_URL=https://api.deepseek.com
LLM_LIGHT_MODEL=deepseek-v4-flash
LLM_HEAVY_MODEL=deepseek-v4-flash

# 鍥剧墖瀹℃煡鐢?VISION_API_KEY=浣犵殑API_KEY锛堝拰涓婇潰鍙互涓€鏍凤級
VISION_BASE_URL=https://api.deepseek.com
```

### 3.2 绫荤洰鍒楄〃

鍦ㄩ」鐩洰褰曚笅鍒涘缓 `config/category_list.json`锛?
```json
{
  "categories": ["绔ヨ", "浜旈噾", "鐧捐揣", "3C", "鏈嶈", "椋熷搧", "缇庡", "瀹跺眳", "姣嶅┐", "鎴峰", "瀹犵墿", "鍏朵粬"],
  "keywords": {}
}
```

鍙互鎸変綘鐨勫疄闄呯被鐩慨鏀癸紝涓嶉渶瑕佹敼浠ｇ爜銆?
---

## 4. 娴忚鍣ㄨ缃?
### 瀹夎 Playwright 娴忚鍣?
```
playwright install chromium
```

### 鍚姩 Chrome 璋冭瘯妯″紡

鍏堟壘鍒?Chrome 瀹夎璺緞锛堥€氬父鏄?`C:\Program Files\Google\Chrome\Application\chrome.exe`锛夛紝鐒跺悗鐢ㄨ皟璇曟ā寮忓惎鍔細

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\chrome-debug"
```

**绗竴娆″惎鍔ㄥ悗锛?*
- 鎵嬪姩鎵撳紑浣犵殑 ERP 缃戠珯
- 鐧诲綍浣犵殑 ERP 璐﹀彿
- 鎵撳紑閲囬泦绠遍〉闈?- 纭椤甸潰鏍囬鎴?URL 鍖呭惈 "collect" 鎴?"閲囬泦"

浠ュ悗鍐嶇敤灏卞彧瑕佸惎鍔ㄨ繖涓揩鎹锋柟寮忓氨琛屻€?
### 绔彛璇存槑

浠ｇ爜榛樿鎵弿 9222-9229 绔彛锛屾墍浠ヤ綘鐢?9223 娌￠棶棰樸€傚鏋滀綘鏀圭鍙ｏ紝鍦ㄥ惎鍔ㄥ懡浠ら噷淇濇寔 `--claim-to` 鏃跺姞 `--cdp-port` 鍙傛暟銆?
---

## 5. 搴楅摵鏄犲皠琛?
鍦ㄩ」鐩洰褰曚笅鍒涘缓 `config/store_category_map.json`锛?
```json
{
  "闋嗛爢銇皬灞嬬瑁濓紙浣犵殑搴楀悕瑕佽窡ERP寮圭獥瀹屽叏涓€鑷达級": ["绔ヨ", "鏈嶈"],
  "浜旈噾搴楀悕": ["浜旈噾", "瀹跺眳"],
  "浣犵殑鍙︿竴涓簵": []
}
```

**瑙勫垯锛?*
- 搴楅摵鍚嶅繀椤讳笌 ERP 璁ら寮圭獥閲岀殑鍚嶅瓧**涓€妯′竴鏍?*锛屽寘鎷嫭鍙峰拰绌烘牸
- 鍙充晶鏁扮粍鏄繖瀹跺簵鍗栧摢浜涚被鐩?- 绫荤洰鍚嶅繀椤诲拰 `category_list.json` 閲岀殑鍚嶅瓧涓€鑷?- 绫荤洰涓嶅啓鍒欒繖瀹跺簵涓嶈嚜鍔ㄥ垎閰嶄换浣曞晢鍝?
---

## 6. 杩愯

棣栨杩愯锛屽厛璇曡瘯鏈€鍩烘湰鐨勬祦绋嬶細

```powershell
cd ~/.openclaw/workspace/cross-border-erp-agent-new
$env:PYTHONIOENCODING='utf-8'

# 娓呯姸鎬?Remove-Item -Force .claim_state.json -ErrorAction SilentlyContinue

# 鍏堢湅鐪嬫晥鏋滐紙dry-run锛屼笉璁ら锛?python run_workflow.py --claim-to "浣犵殑搴楅摵鍚?
```

濡傛灉绋嬪簭鎶?"Chrome CDP 鏃犳硶杩炴帴"锛岃鏄?Chrome 璋冭瘯妯″紡娌″惎鍔ㄣ€?
### 甯歌闂

| 闂 | 鍘熷洜 | 瑙ｅ喅 |
|------|------|------|
| Chrome CDP 杩炰笉涓?| Chrome 娌′互璋冭瘯妯″紡鍚姩 | 鎸夌4鑺傞噸鏂板惎鍔?Chrome |
| API Key 鎶ラ敊 | .env 娌￠厤鎴栭厤閿?| 妫€鏌?.env 鏂囦欢 |
| 鎵句笉鍒板簵閾?XXX | 搴楀悕鍜孍RP寮圭獥瀵逛笉涓?| 鍏堣窇涓€娆?--list-stores 鐪嬬湅寮圭獥閲屾樉绀虹殑搴楀悕 |
| 绫荤洰璇嗗埆涓嶅噯 | 绫荤洰鍒楄〃澶 | 淇敼 config/category_list.json 缂╁皬鑼冨洿 |
| UncodeDecodeError | 缂栫爜闂 | 鍏堣窇 `$env:PYTHONIOENCODING='utf-8'` |
