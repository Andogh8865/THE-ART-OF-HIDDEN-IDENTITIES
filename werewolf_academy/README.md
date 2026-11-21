# ☾ Werewolf Academy

**LLM Wiki × Interactive Teaching HTML Slides × Evidence-First Graph**

> 12 人狼王守衛局新手課程。包含 10 頁 HTML 簡報、7 份來源的整理證據、18 條可追溯規則、角色翻牌、夜間模擬與互動問答。所有站點內容可部署至 GitHub Pages。

## 專案成果與直接開啟

- **互動簡報**：`index.html`（在瀏覽器雙擊開啟，按左右鍵切換）
- **Wiki**：`wiki/index.html`（搜尋、來源追溯、版本衝突對照）
- **流程圖與反思**：`docs/graph.md`
- **來源與證據**：`data/source_evidence.json`（7 個來源、33 條整理證據）
- **Wiki 核對規則**：`data/verified_claims.json`（18 條）
- **執行紀錄**：`logs/run_v1.json`、`logs/run_v2.json`、`logs/comparison.json`、`logs/ui_tests.json`（16/16 Chrome UI 驗證）
- **程式與測試**：`pipeline/graph.py`、`pipeline/build_site.py`、`tests/`

## 一分鐘操作

```bash
# Python 3.10+；基礎 Graph 不需 pip 安裝
python pipeline/graph.py --demo-both

# 本機開啟網站；亦可直接開 index.html
python -m http.server 8000
# 瀏覽 http://localhost:8000/
# Wiki: http://localhost:8000/wiki/
```

## Graph 的真實執行

`graph.py` 的節點、條件邊、修復循環都是實際 Python 程式，不是只有圖。V1（無前置分類）與 V2（先分類再生成）在**相同 7 來源 / 18 規則**的固定資料上執行。V1 初次簡報 QA 發現 3 條跨版本規則，進入修復 Loop；V2 在 Wiki 建置之前已分出三種不同版本差異，初次 QA 沒有這些錯誤。詳細數字與反思見 `docs/graph.md`。

## 資料取得範圍與 AI 使用說明

初始 Wiki 在 ChatGPT 協助下，透過逐頁查閱 7 個公開來源、辨識差異、整理為 **短篇原創轉述的 evidence records** 建立。`source_evidence.json` 是可檢查的**已整理來源證據**，不是把七篇完整文章打包，也不是此環境自行爬取七個網站的結果。由於本次執行環境無法直接存取網站，`fetch_sources.py` **尚未執行成功取得完整原始 HTML**。若老師嚴格要求自動抓取原始全文，請在有網路的電腦執行：

```bash
python pipeline/fetch_sources.py
```

此工具會真正發出 HTTP 請求、解析頁面文字、記錄來源是否擷取成功、字數與雜湊；只儲存稽核紀錄，避免重新發布原作者全文。需確認至少 5 篇成功後再將 `logs/fetch_audit.json` 放入繳交資料。部分網站可能有反爬限制，應換可存取來源或經合法方式手動匯入。

如果希望執行真正的 **LLM 校驗節點**（需自備 API Key）：

```bash
# Linux/macOS
export OPENAI_API_KEY='your-key'
python pipeline/llm_review.py
```

`llm_review.py` 對各 Claim 與對應 evidence 做 grounded review，輸出 `logs/llm_review.json`，不會擅自覆蓋已核准的規則。**本包附的 Demo 執行紀錄不宣稱曾呼叫外部 LLM API。**

## 實際 UI 測試

本次以 Chromium + Playwright 實際執行 16 項操作測試：切頁、角色卡、夜晚結算、連守驗證、用藥、測驗、Wiki 搜尋、手機寬度，以及 JavaScript 錯誤檢查；結果見 `logs/ui_tests.json`。

如需重跑：先安裝 `pip install playwright` 並安裝 Chromium（必要時執行 `playwright install chromium`），再執行 `python tests/browser_smoke.py`。

## 如何部署 GitHub Pages

1. 在 GitHub 建立新的公開 Repository（例如 `werewolf-academy`）。
2. 將此資料夾內容上傳至 Repo 根目錄；確認 `index.html` 在最外層。
3. Repository → **Settings → Pages** → Build and deployment: **Deploy from a branch**。
4. 選擇 `main` 分支、`/(root)`，儲存；GitHub 之後會提供正式網站網址。
5. 檢查 `/` 是簡報、`/wiki/` 是知識庫、三項互動是否正常。

只要網站部署完成，簡報和 Wiki 不需要伺服器或 API Key 即可瀏覽；全站沒有外部字型或 JavaScript 依賴。

## 繳交檢查

- [x] LLM Wiki 主題與介紹
- [x] 七個已審閱來源的整理證據與 Wiki 成品
- [x] 可離線瀏覽的教學 HTML（10 頁）
- [x] 可執行 Graph 與 Mermaid 流程圖
- [x] V1/V2 實際執行紀錄、檢查結果與反思
- [ ] 公開 GitHub Pages URL（須上傳後取得）
- [ ] 若需嚴格完整網頁自動 Ingest，須於可連網環境跑 `fetch_sources.py`

## 技術

- HTML / CSS / Vanilla JavaScript：無框架、無 API Key、無必須的 CDN JS
- Python 3.10+ 標準函式庫：可執行 Graph、核對、生成 HTML
- 可選外部 LLM review 與線上來源取得；基礎成果不依賴它們
- 來源引用：每個 Claim 有 C-ID → Evidence ID → Source ID → URL

**注意**：狼人殺有房規與板子版本差異。此作品採固定的 12 人狼王守衛示範規則，不代表所有社群都採用相同設定。
