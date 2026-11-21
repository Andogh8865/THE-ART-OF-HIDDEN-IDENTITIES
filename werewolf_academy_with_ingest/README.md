# ☾ Werewolf Academy

**LLM Wiki × Interactive Teaching HTML Slides × Evidence-First Graph**

> 12 人狼王守衛局新手課程。包含 10 頁 HTML 簡報、7 份來源的整理證據、18 條可追溯規則、角色翻牌、夜間模擬與互動問答。所有站點內容可部署至 GitHub Pages。

## 專案成果與直接開啟

- **互動簡報**：`index.html`（在瀏覽器雙擊開啟，按左右鍵切換）
- **Wiki**：`wiki/index.html`（搜尋、來源追溯、版本衝突對照）
- **流程圖與反思**：`docs/graph.md`
- **已執行的來源 Ingest**：`ingest_report.html`（7 篇來源摘記成功，16 段知識，33 條證據）
- **來源原始輸入**：`data/source_inputs/S01.json`～`S07.json`（7 份獨立、核對後轉述的來源筆記）
- **匯入後知識庫**：`data/ingested_sources.json`、`data/source_chunks.json`
- **Wiki 核對規則**：`data/verified_claims.json`（18 條）
- **執行紀錄**：`logs/run_v1.json`、`logs/run_v2.json`、`logs/comparison.json`、`logs/ui_tests.json`（16/16 Chrome UI 驗證）
- **程式與測試**：`pipeline/graph.py`、`pipeline/build_site.py`、`tests/`

## 一分鐘操作

```bash
# Python 3.10+；不需要額外 pip 安裝
python pipeline/ingest_sources.py
python pipeline/graph.py --demo-both

# 本機開啟網站；亦可直接開 index.html
python -m http.server 8000
# 瀏覽 http://localhost:8000/
# Wiki: http://localhost:8000/wiki/
# Ingest 紀錄: http://localhost:8000/ingest_report.html
```

## Graph 的真實執行

`graph.py` 的節點、條件邊、修復循環都是實際 Python 程式，不是只有圖。V1（無前置分類）與 V2（先分類再生成）在**相同 7 來源 / 18 規則**的固定資料上執行。V1 初次簡報 QA 發現 3 條跨版本規則，進入修復 Loop；V2 在 Wiki 建置之前已分出三種不同版本差異，初次 QA 沒有這些錯誤。詳細數字與反思見 `docs/graph.md`。

## 資料 Ingest：已實際執行（注意資料範圍）

**新版 Ingest 已確實運作，並非只統計參考文獻網址。** 七個公開網頁在查閱後，整理為七份各自獨立的中文原創來源筆記（`data/source_inputs/S01.json`～`S07.json`），每份包含網址、規則版本、經核對的敘述與來源證據。執行 `pipeline/ingest_sources.py` 後，程式會依序：

1. 開啟七份來源筆記檔案並驗證 ID、HTTPS 網址、文字與證據格式。
2. 拆成可檢索的文字段落，計算 SHA-256 供追查內容版本。
3. 將來源與觀察正規化為 `data/ingested_sources.json`，建立 `data/source_chunks.json`。
4. 產生 `logs/ingest_run.json` 和可供老師點閱的 `ingest_report.html`；少於五篇有效來源會失敗，不會虛報通過。
5. `pipeline/graph.py` **直接讀入這次產生的資料與 Log**，再進行版本分類、18 條 Claim 核對及 HTML 簡報生成。

本次實測：**7/7 份來源摘記成功、16 個知識段落、33 條來源證據**。結果可在 `logs/ingest_run.json` 查看。

**範圍限制（繳交時請保留）**：這裡匯入的是「七篇網站的人工核對、AI 協助整理之來源摘記」，**不是直接 HTTP 抓下七篇原始完整網頁全文**。原因是本次程式執行環境無法直接連外網。如果老師嚴格要求網頁全文自動抓取，請在有網路的電腦另外執行 `python pipeline/fetch_sources.py`，確認 `logs/fetch_audit.json` 至少五筆 `FETCHED`；該工具是全文取得的**稽核步驟**，不應把 HTTP 存取成功與完成 Wiki 規則驗證混為一談。

另外 `pipeline/llm_review.py` 可以用自備 API Key 做 LLM 二次證據校驗，未在本次紀錄中冒稱已呼叫外部 LLM API。

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
- [x] 七份來源摘記的實際 Ingest、可追溯證據與 Wiki 成品
- [x] 可離線瀏覽的教學 HTML（10 頁）
- [x] 可執行 Graph 與 Mermaid 流程圖
- [x] V1/V2 實際執行紀錄、檢查結果與反思
- [ ] 公開 GitHub Pages URL（須上傳後取得）
- [ ] 若老師要求原始網頁**完整全文**自動擷取，須於可連網環境另外跑 `fetch_sources.py`

## 技術

- HTML / CSS / Vanilla JavaScript：無框架、無 API Key、無必須的 CDN JS
- Python 3.10+ 標準函式庫：可執行 Graph、核對、生成 HTML
- 可選外部 LLM review 與線上來源取得；基礎成果不依賴它們
- 來源引用：每個 Claim 有 C-ID → Evidence ID → Source ID → URL

**注意**：狼人殺有房規與板子版本差異。此作品採固定的 12 人狼王守衛示範規則，不代表所有社群都採用相同設定。
