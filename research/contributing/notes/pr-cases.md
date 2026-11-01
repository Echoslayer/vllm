# 六個 PR 案例：維護者實際接受什麼證據？

查核日：2026-11-01。這是第一輪質性研究，供第一次貢獻者選擇驗證方式，不估計合併機率。

**先看修正能證明哪個使用者行為，再決定測試範圍。** 這批案例包括一行正式程式修改、跨線上與離線路徑的修正，以及由別人整合落地的貢獻；「改動小」不等於「只驗證一個私有函式」。[案例 #64032](https://github.com/vllm-project/vllm/pull/64032)、[案例 #61986](https://github.com/vllm-project/vllm/pull/61986)、[整合案 #56844](https://github.com/vllm-project/vllm/pull/56844)

## 怎麼選樣與查核

- 目的取樣：從既有[專案選擇調研](../../oss-candidates/vllm-llamacpp.md)挑四件多模態修正，以及兩件結果不同的關閉案。這不是隨機樣本，也不是某期間的完整母體。
- 每件主案例都透過 GitHub REST API 重新讀取 PR 描述、所有一般留言、所有 reviews、所有逐行評論與完整 changed-files 清單；清單使用分頁擷取。下表記錄實際取得的筆數。
- 已讀所有主案例的最終 patch，並核對所引用的人類審查意見。bot 長篇說明只用來辨識討論脈絡，不當成維護者結論。
- 另查兩件關閉案的標籤與關閉事件，以及替代 PR #56844 的描述與合併狀態。未完整審查 #56844 的 diff 或討論。
- GitHub 網頁可讀，但搜尋服務顯示的 #55836 快取仍為 draft；本筆記以本次 REST API 回覆為狀態依據，沒有沿用快取狀態。
- API 的 `author_association` 是查核當下值；本輪未查作者提交前的歷史，不能把 `CONTRIBUTOR` 當成當時已是常客。
- 精簡快照見 [pr-case-evidence.json](pr-case-evidence.json)：保存 URL、head SHA、日期、狀態、檔案規模、評論索引及擷取筆數，不複製整段描述或帳號 email。

## 案例總表

日期為 UTC；「+／−」包含測試與文件，是本次 API 回覆的完整 diff 規模。

| PR | 查核時結果 | 合併或關閉日期 | 規模 | 本次觀察重點 |
| --- | --- | --- | --- | --- |
| [#62704：損壞 PNG](https://github.com/vllm-project/vllm/pull/62704) | 已合併 | 2026-10-22 | +19／−1，2 檔 | 真實壞輸入、HTTP 前後對照、補註解 |
| [#64032：停用本機媒體](https://github.com/vllm-project/vllm/pull/64032) | 已合併 | 2026-10-27 | +34／−3，3 檔 | Mac CPU 手動驗證與 GPU 回歸測試分開交代 |
| [#53744：錯誤 base64 音訊](https://github.com/vllm-project/vllm/pull/53744) | 已合併 | 2026-08-25 | +13／−1，2 檔 | 一行修正；揭露環境造成的既有測試失敗 |
| [#61986：RGB PNG 透明度](https://github.com/vllm-project/vllm/pull/61986) | 已合併 | 2026-10-16 | +102／−16，6 檔 | 審查要求線上、離線輸入保持一致 |
| [#55836：gRPC 文件](https://github.com/vllm-project/vllm/pull/55836) | 關閉未合併 | 2026-09-08 | +2／−2，1 檔 | 有 approval，仍被關閉；具體理由未說明 |
| [#55765：prompt offset](https://github.com/vllm-project/vllm/pull/55765) | 關閉未合併 | 2026-09-15 | +76／−7，4 檔 | 另一件 PR 整合，原作者被列入貢獻名單 |

## 1. #62704：一行例外處理，也要說清楚使用者會看到什麼

**已查證的 diff：** 在 `ImageMediaIO.load_bytes` 既有例外處理加入 `SyntaxError`，並用實際損壞 PNG 位元組新增回歸測試。沒有另建錯誤處理架構。[最終 diff](https://github.com/vllm-project/vllm/pull/62704/files)

**作者提出的驗證：** CPU 單元測試 20 件通過；另在 H100 部署比較壞 PNG、正常 PNG 與隨機位元組的 HTTP 結果。壞 PNG 從 500 變成 400，其餘兩種維持原結果。這是作者報告，不是本研究重跑。[PR 描述](https://github.com/vllm-project/vllm/pull/62704)

**實際審查：** DarkLight1337 要求補一句程式註解，解釋 Pillow 的例外；作者補完後獲批准。維護者還重試 CI，最後對另一個 head 再觸發執行。[註解要求](https://github.com/vllm-project/vllm/pull/62704#discussion_r4335519189)、[批准](https://github.com/vllm-project/vllm/pull/62704#pullrequestreview-5599702502)、[最後一次 CI 觸發](https://github.com/vllm-project/vllm/pull/62704#issuecomment-6333490480)

**本書推論：** 可模仿的是「壞輸入 → 既有處理漏接 → 對外行為 → 正常輸入不退化」這條證據鏈，不能只模仿多加一個例外類型。

## 2. #64032：Mac 可以提供證據，但要說明沒有跑到哪裡

**已查證的 diff：** 當伺服器未允許本機媒體時，把 `RuntimeError` 改成現有的 `VLLMValidationError`；更新同步／非同步 connector 測試，另補 render HTTP 入口回歸測試。[最終 diff](https://github.com/vllm-project/vllm/pull/64032/files)

**作者提出的驗證：** 在 macOS arm64 CPU build，以 SmolVLM 實際比較 HTTP 500 與 400，另報告 94 件媒體測試通過。新增 render 測試沿用 Qwen 視覺伺服器 fixture，需要 GPU，作者明說沒有在本機執行，而以較小模型手動查同端點。[PR 描述](https://github.com/vllm-project/vllm/pull/64032)

**實際審查：** DarkLight1337 批准並觸發 CI；本次沒有逐行評論。資料可以支持「該次驗證說明獲接受」，不能推出所有 GPU 測試皆可免跑。[批准](https://github.com/vllm-project/vllm/pull/64032#pullrequestreview-5666617317)、[CI 指令](https://github.com/vllm-project/vllm/pull/64032#issuecomment-6441228226)

**本書推論：** 先找到成本可負擔的真實入口，再誠實列出模型、端點與 CI 覆蓋差異，會比只說「CPU 測試通過」更具體。

## 3. #53744：把環境失敗與新回歸分開報告

**已查證的 diff：** 音訊 base64 解碼補上既有其他媒體使用的 `validate=True`，並在合法音訊編碼中插入非法字元，確認 loader 拒絕輸入。[最終 diff](https://github.com/vllm-project/vllm/pull/53744/files)

**作者提出的驗證：** 新測試在原版失敗、修正版通過。較大媒體測試集仍有 71 件失敗：修正版 43 件通過，原版 42 件通過。作者歸因於缺少 `cv2`、資產或網路，並揭露未跑效能／準確率測試。[PR 描述](https://github.com/vllm-project/vllm/pull/53744)

**實際審查：** Isotr0py 批准並觸發 CI；沒有逐行討論。這不能證明失敗項目可一概忽略，也不能把作者的環境歸因視為本研究已獨立驗證。[批准](https://github.com/vllm-project/vllm/pull/53744#pullrequestreview-5021304697)、[CI 指令](https://github.com/vllm-project/vllm/pull/53744#issuecomment-5413403712)

**本書推論：** 遇到既有失敗時，保留相同環境的原版／修正版比較，比把失敗刪掉或只報新增測試通過更有用。

## 4. #61986：審查改變的是要維持的行為，不只是寫法

**已查證的 diff：** RGB PNG 的透明色不再被同模式提早返回略過；兩條影像載入路徑共用轉換邏輯，並補背景色、快取與線上／離線一致性測試，更新透明度文件。[最終 diff](https://github.com/vllm-project/vllm/pull/61986/files)

**實際審查：** bot 指出 GIF 轉 RGB 後留下透明資訊的情況。作者先把處理限縮到載入檔案的路徑；DarkLight1337 隨後要求比較線上與離線流程。作者確認限縮版本造成兩者不同，於是回到共用轉換位置並改測試。[維護者要求](https://github.com/vllm-project/vllm/pull/61986#discussion_r4293052333)、[作者修正說明](https://github.com/vllm-project/vllm/pull/61986#discussion_r4297321943)

**作者提出的驗證：** 相關 CPU 測試從 6 失敗、51 通過變成 57 通過；另以 L4 與 Qwen 比較實際模型回答及像素差異。測試結果均未由本研究重跑。[PR 描述](https://github.com/vllm-project/vllm/pull/61986)

**本書推論：** 當修改改變送進模型的像素，單一格式或單一路徑的測試不夠；要先列出所有入口和預期一致性。這也說明 bot 建議應驗證，不能直接當成最終設計。

## 5. #55836：approval 不保證合併；關閉原因不能腦補

**已查證的 diff：** 只有安全文件兩處修改，將不存在的 `--grpc-port` 說法改成 `--grpc` 與共用連接埠參數。作者附原始碼查核步驟，但測試計畫仍未勾選。[最終 diff](https://github.com/vllm-project/vllm/pull/55836/files)、[PR 描述](https://github.com/vllm-project/vllm/pull/55836)

**實際紀錄：** jperezdealgaba 留下批准；同日 hmellor 加上 `closed-as-slop` 標籤並關閉。完整一般留言只有兩則 bot 訊息，沒有解釋該標籤的人工留言。[批准](https://github.com/vllm-project/vllm/pull/55836#pullrequestreview-5138422979)、[事件 API](https://api.github.com/repos/vllm-project/vllm/issues/55836/events)

**不能下的結論：** 無法從這一件判定「文件都不收」、「因 AI 而關」或「修改內容錯誤」。標籤揭示處置分類，沒有揭示具體理由。

**本書推論：** 選題時仍需說明整體使用者價值；不要把某人的 LGTM 當成維護者團隊的最終承諾。

## 6. #55765：關閉未合併，也可能已有成果落地

**已查證的原案：** 修改 prompt offset 邊界並增加驗證與測試。後續出現合併衝突提示，再由 aoshen02 關閉。[原案 diff](https://github.com/vllm-project/vllm/pull/55765/files)、[關閉事件](https://api.github.com/repos/vllm-project/vllm/issues/55765/events)

**有直接留言的原因：** aoshen02 說明改由 #56844 修復，並將原作者列為共同作者。#56844 描述也列出 #55764、#55765 的貢獻來源；API 確認它於 2026-09-15 合併。[關閉說明](https://github.com/vllm-project/vllm/pull/55765#issuecomment-5673722007)、[替代 PR](https://github.com/vllm-project/vllm/pull/56844)

**範圍限制：** 本研究確認的是公開描述有列名及替代案已合併，沒有核對 Git commit 的 coauthor trailer，也未逐行判定原案多少程式碼被採用。

**本書推論：** 研究成果應分開記錄「自己的 PR 是否合併」和「問題是否經其他 PR 解決」，否則會把整合落地算成純粹失敗。

## 下一輪收集什麼

下列是研究建議，不是官方要求，也不代表已認領工作。

1. 先從一條可公開重現的媒體輸入路徑建立本機基線，記錄安裝方法、資產來源、通過與失敗項目。
2. 若要研究「哪些外部貢獻較容易合併」，另訂固定取樣期間，包含仍開啟與關閉案；本次六件不能當分母。
3. 若要研究「先開 issue 是否有幫助」，逐件讀連結議題的建立時間與互動，不能只數 PR body 有沒有 `Fixes`。
4. 若要研究「點名 reviewer 是否有效」，收集相近內容與規模的未點名對照組；#61986 的單次點名不能證明因果。
5. 正式選題前重查當時的 open PR 與目前程式碼。本篇描述的是已結案案例，不是待修清單。

## 擷取完整度與限制

「一般留言」不含 PR 描述；「reviews」包含批准及 bot review；「逐行評論」可能屬於同一則 review，因此不能相加當成互動次數。

| PR | 一般留言 | reviews | 逐行評論 | 檔案 |
| --- | ---: | ---: | ---: | ---: |
| #62704 | 11 | 4 | 2 | 2 |
| #64032 | 3 | 2 | 0 | 3 |
| #53744 | 2 | 2 | 0 | 2 |
| #61986 | 6 | 7 | 4 | 6 |
| #55836 | 2 | 1 | 0 | 1 |
| #55765 | 4 | 2 | 1 | 4 |

本輪未重跑程式、下載模型、讀完整 CI log、驗證硬體數字，或調查 Slack 私下互動。沒有計算作者首次貢獻身分、等待時間母體或合併率。

歷史 PR 的測試命令反映作者當時環境，不應直接複製作為目前 vLLM 的安裝指南；應先讀目前版本的貢獻規則和測試說明。

### 精簡快照能重算什麼？

JSON 保留六件 PR 的狀態、日期、作者帳號與當下關聯、head SHA、標籤、增刪行數，以及全部評論的 URL、時間、作者與 review state 索引。另保留每檔增刪行數、兩件關閉案的選定事件及 #56844 的合併資料。

因此可離線重算本篇的案例數、狀態、規模與擷取筆數，不能離線重建評論文字、PR 描述、patch 或 CI 結果。`body_sha256` 只能核對重新取得的描述是否與查核時一致，不能還原描述。

若要重查文字，依案例編號重新讀 GitHub REST 的 `pulls/{number}`、`issues/{number}/comments`、`pulls/{number}/reviews`、`pulls/{number}/comments`、`pulls/{number}/files`，各清單須處理全部分頁。討論可能編輯或刪除，重新擷取不保證還原歷史全文；本篇的文字判讀仍需對照所附原始連結。
