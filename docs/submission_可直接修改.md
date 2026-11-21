# 【學校】【學號】【系級】【姓名】｜Werewolf Academy：LLM Wiki × 互動教學簡報

## 1. LLM Wiki 主題與簡短介紹

我以「12 人狼王守衛局」為主題製作 Werewolf Academy，目標是讓從未玩過狼人殺的新手了解角色、日夜流程、屠邊勝利條件及夜間技能互動。由於不同來源常使用不同板子／房規，本專案特別把來源標記成 `WKG12`、`GENERAL_LANGRENSHA`、`JINRO_BROWSER` 與 `MILLERS_HOLLOW`，避免混淆。

## 2. Wiki 成果

- Wiki：`wiki/index.html`／（部署後填入網址）【WIKI_URL】
- Ingest 報告：`ingest_report.html`／（部署後填入網址）【INGEST_URL】。
- 真正執行 Python Ingest：成功讀入 **7 份獨立來源摘記**，產生 **16 個知識段落、33 條來源證據、18 條已核對 Claim**。
- 執行紀錄：`logs/ingest_run.json`、`data/ingested_sources.json`、`data/source_chunks.json`。
- 資料範圍：摘記經逐頁核對後重新撰寫，**不是自動 HTTP 下載七篇原始全文**。
- 每條 Claim 都有 `C-ID → Evidence ID → Source ID → 原始 URL` 的追溯關係。

## 3. HTML 教學簡報

- 簡報：`index.html`／（部署後填入網址）【SLIDES_URL】
- 共 10 頁，包含角色卡翻轉、夜晚行動模擬、3 題知識測驗及每頁證據標籤。

## 4. Loop / Graph 設計

`Read 7 source notes → Validate / Chunk / Index → Extract → Classify versions → Evidence QA → Wiki → Slide Planner → Draft Slides → Content QA → HTML → HTML QA → Publish`。

如果內容 QA 發現違反板子設定的 Claim，就回到 `Repair Draft`，查回主板的 evidence 重新建立該段內容，再回到 QA。缺乏有效證據則停止等待人工處理，避免憑空生成。圖在 `docs/graph.svg`、詳細解釋在 `docs/graph.md`。

## 5. 實際執行與檢查結果

先執行 `python pipeline/ingest_sources.py`（成功 7/7），再執行 `python pipeline/graph.py --demo-both`，同一組已審核證據的受控對照結果：

- V1（未在 Wiki 前做版本分類）：第一次 Content QA 偵測 **3** 個跨版本錯誤，修復 **3** 個 Claim，QA 執行 **2** 次。
- V2（先做板子版本分類及 Evidence QA）：不同版本證據 **3** 筆先行標記與分流，第一次 Content QA **0** 個版本混用錯誤，QA 執行 **1** 次。
- HTML 及 UI 實際測試通過 **16/16** 項，測試內容涵蓋切頁、角色翻轉、守衛連守、同守同救、女巫行動、測驗及搜尋。
- Ingest 真實執行紀錄：`logs/ingest_run.json`（7 份輸入、16 段索引、33 筆證據）。
- 原始執行紀錄：`logs/run_v1.json`、`logs/run_v2.json`、`logs/comparison.json`、`logs/ui_tests.json`。

**方法註記：** 本專案已實際讀入七份來源摘記；摘記由公開網頁核對後整理，並非自動下載的七份原始全文。V1/V2 數字是固定證據集上的 workflow 消融示範，不是泛化的 LLM 效能實驗。若需要實際網址抓取稽核，請在可上網環境執行 `python pipeline/fetch_sources.py`。

## 6. 反思

最容易出問題的是 **V1 的 Wiki 建立節點**：只讀到同一題的第一個來源就採信，導致「狼人追平人數勝利」「第一夜不淘汰玩家」「守衛能否連守」等不同規則版本混入本次 12 人狼王守衛教材。後面的 Slide QA 才發現時，已經需要修正生成內容。

我因此在 V2 把檢查從 **簡報草稿之後前移到 Wiki 建置之前**：先判斷 Evidence 的板子 Scope，再核對 Claim 是否有對應的來源支持，確認無誤才讓它進入 Wiki 與簡報。這樣可避免錯誤內容沿著流程擴散；在本次受控測試中，晚期的版本混用錯誤從 3 個降為 0。

## 附件

`README.md`、`docs/graph.svg`、`docs/graph.md`、`docs/discussion-before-generation.md`、`logs/`、網站程式及證據資料。
