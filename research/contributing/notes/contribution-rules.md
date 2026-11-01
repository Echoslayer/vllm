# vLLM 貢獻規則：先準備可驗證的問題，再請維護者審查

查核日：2026-11-01。這是第一輪資料筆記，供準備第一次貢獻的讀者使用。

**最重要的差異是：vLLM 明文要求揭露 AI 協助與 commit attribution；CI 也不會因每次推送就完整執行。** 先找有實際影響、能重現的問題，再確認驗證成本。不要把 Ultralytics 的流程或行數門檻搬過來。[官方規範][agents]、[貢獻指南][contributing]

## 這一輪查了什麼

- 本機 `origin/main` 與 GitHub REST `commits/main` 都是 `5d55ef1590c92213e3893dc8e8712f7f2e0bc508`。
- 已讀官方規範、貢獻指南、PR 模板、`pr-checklist`、治理文件，以及 pre-commit、CI 指令與 stale 工作流程。
- 另以網頁開啟官方 `AGENTS.md`，確認主要規則與本機快照一致。
- 以下來源固定到該 commit；發布後的新規則不會自動反映在筆記裡。

本文標記的意思：**要求**是官方明文規則；**建議**是官方使用 recommend、should 或流程期望的內容；**研究判斷**是本書根據來源提出的做法。

## 1. 哪些工作算貢獻

官方歡迎回報問題、新模型、新功能、文件與教學，也把回答問題、審查 PR 和協助社群視為貢獻。這不是「必須先送 code 才算參與」。[指南開頭與 Job Board][contributing]

但 AI 輔助貢獻另有品質要求：不可送純 agent PR；人要讀懂每一行、實際驗證並能負責。單一拼字、孤立的格式整理或單一 mutable default 修正等零碎忙工，不應各自開 PR。這不等於全面禁止文件貢獻。[AI 規範][agents]、[治理 AI 政策][governance]

**研究判斷：** 第一題應能回答「誰在什麼輸入下遇到什麼問題、修改後如何證明改善」。程式碼少，只能降低閱讀成本，不能單獨證明貢獻有價值。[設計與證據檢查][checklist]

## 2. 要不要先開 issue 或 RFC

| 情況 | 來源實際說法 | 下一步 |
| --- | --- | --- |
| 遇到 bug 或有功能需求 | 指南要求先搜尋既有 issue；沒有相同回報時，請提供相關資訊建立新 issue | 先搜尋問題、錯誤訊息與子系統 |
| 準備 AI 輔助 PR | 要查 issue 留言、引用該 issue 的 open PR，以及相同領域關鍵字 | 已有相同修正就不重複開 PR；做法實質不同，先在 issue 說明 |
| 重大新功能 | 協作政策要求先提出 RFC，不以行數為前提 | 使用 RFC issue 模板，說明動機、問題、替代方案與設計，再到 Slack `#contributors` 請 area owner 與 committer 回饋 |
| 重大架構變更 | 超過 500 LOC，且排除 kernel、data、config、test，預期先有討論設計與理由的 GitHub RFC | 缺 RFC 可能被標 `rfc-required` 並不予處理 |
| 小型修正是否一律要 issue 核准 | 本次讀到的文件沒有寫「每一筆 PR 必須先取得 issue 核准」 | 不把這個缺少明文的條件當成官方許可；有範圍疑慮先討論 |

來源：[Issues 與大型變更規則][contributing]、[重大功能協作政策][collaboration]、[查重要求][agents]。

**研究判斷：** 「先搜尋／回報」和「先取得維護者批准」是不同條件。不要把一般小修正套成必須等 RFC，也不要因重大新功能少於 500 行就跳過 RFC。[指南][contributing]、[協作政策][collaboration]

安全漏洞有獨立通報管道，應依 [SECURITY.md][security]，不以一般公開 bug 流程處理。

## 3. AI、DCO 與提交內容

| 項目 | 要求 | 容易誤會的地方 |
| --- | --- | --- |
| 人的責任 | 人要理解改動、讀過所有修改行並執行相關驗證 | AI 產出和綠燈 CI 都不能代替人的確認 |
| PR 揭露 | PR 描述需聲明 AI 協助；模板另有 AI 使用勾選欄 | 不只是在聊天裡說用過 AI |
| Commit attribution | 使用適當 trailer，例如 `Co-authored-by:` | 不能沿用其他專案的「不放 AI 標註」習慣 |
| DCO | 提交者同意 DCO，每筆 commit 要有 `Signed-off-by:`；`git commit -s` 可加入 | DCO sign-off 與 AI attribution 是不同欄位 |
| 範本 | 保留 Overview、Claims、Validation、Details 與 checklist | 長日誌可連結或折疊，不要塞滿摘要 |

來源：[AI 與 DCO 規則][contributing]、[DCO 原文][dco]、[PR 模板][template]、[PR 內容檢查][checklist]。

本筆記只整理提交流程，不替提交者判定其授權、雇傭關係或 DCO 資格；正式提交前由本人讀原文並確認。

對 AI agent，開 PR（含 draft）或請求重新審查前，必須執行 vLLM 的 `pr-checklist` 並處理發現。人類手動使用則在模板標為 optional。[規範][agents]、[模板][template]

## 4. PR 標題、大小與驗證

**要求：** 標題開頭是一個或多個方括號標籤，再接空格和簡短描述。可用 `[Bugfix][Multimodal] ...`；指南接受有描述性的標籤，列出的標籤不是封閉清單。[標題規則][contributing]

**粗略指標，不是硬上限：** `pr-checklist` 把主要程式新增少於 50 行視為低複雜度、50–250 行為中等、超過 250 行為高複雜度，可排除測試與文件。語意複雜度仍須另外判斷；bug fix 跨入高複雜度範圍要充分說明。[複雜度檢查][checklist]

不要把這組數字與「重大架構變更超過 500 LOC 需 RFC」混為同一門檻；兩者用途與排除項目不同。重大新功能另有先提 RFC 的規則，不限行數。[大型變更規則][contributing]、[協作政策][collaboration]

驗證要跟宣稱對應：[驗證與 PR 證據規範][checklist]

- Bug fix：提供可重現案例，說明根因；可重現 bug 的新增測試要展示修改前失敗、修改後通過。
- Serving engine 改動：要端到端驗證；只通過內部 helper 的測試不等於已驗證使用者行為。
- 效能改進：交代模型、硬體、設定、工作負載、基準與修改後結果；只做 microbenchmark 可能不足。
- 模型輸出、準確度或 serving 受影響：附相關模型評估。[補充要求][agents]
- CI 缺硬體或 checkpoint：記錄缺口、資源限制與 CI 外的驗證；不是省略驗證的理由。

**要求：** 使用者可見的行為、參數、預設值等改動，要在同一 PR 更新能呈現給使用者看的文件。只有測試、程式註解或 PR 描述不夠；CLI/config 等參考頁可能由 docstring 或 help 產生。[文件要求][contributing]

## 5. CI 有兩道不同的門

### pre-commit：新作者可能先卡在資格檢查

上游 `pre-commit.yml` 對 PR 檢查是否有 `verified`、`ready` 或 `ready-run-all-tests` 標籤，或作者已在該 repo 合併至少 4 件 PR。沒有符合就讓 pre-run check 失敗，後續 lint 不執行；訊息也要求 AI agent 不要代為索取標籤。[工作流程][precommit]

**研究判斷：** 這種失敗不代表程式已被 lint 判定有錯。要先讀失敗步驟與日誌；本機仍應先跑 pre-commit，不能用遠端未執行當成省略理由。[本機 lint 指南][contributing]

### Buildkite：授權、分支新鮮度、實際跑哪些測試

| 條件 | 已確認的行為 |
| --- | --- |
| 有 write／maintain／admin 權限，或設定為 trusted contributor | 可呼叫 CI 指令 |
| 一般 PR 作者 | PR 不能是 draft；要有 ready 類標籤，或目前 APPROVED 且有可信 reviewer 的有效 approval |
| 只是其他路人的 approval | 不等於具備 CI 授權 |
| 推送新 commit | 不會自動啟動完整上游 CI |
| 分支落後目標分支 | 預設 run 要零落後；bot 會嘗試把目標分支 merge 進 PR，成功後測合併 commit |
| fork 不允許維護者編輯，或有衝突 | 自動更新不能完成，先自行更新再重跑 |
| 同 commit 已有 CI build | 無 write 權限的作者不能再開另一個 full run；可重試失敗工作或請有權限的人處理 |

來源：[review/CI 指南][contributing]、[CI 指令入口][ci-workflow]、[授權實作][ci-script]。

`--allow-stale` 可繞過 run 的新鮮度檢查，但不改授權條件；合併前仍需更新目標分支並在最新 PR commit 重跑。retry/cancel 不查分支新鮮度。[指南][contributing]

**研究判斷：** bot 更新後先 pull，再繼續修改；報告測試結果時記錄 SHA。不要拿舊 commit 的綠燈替現在的改動背書。[分支更新規則][contributing]

指南提醒，聚合狀態的「passed and blocked」不保證必要測試已跑完；CI 指令程式本身也不會設定 GitHub 分支保護。這次未讀管理員設定，不能確認實際 required checks。[合併保護說明][contributing]

## 6. 找誰審、等多久、何時追蹤

- 官方 reviewer 或 committer 都可正式 review，最後由 committer 合併。依專長名單找人，或去 Slack `#pr-reviews` 求助。[review 說明][contributing]
- 治理文件說 PR 至少需一位 committer review 與 approval；涉及 CODEOWNERS 的程式應請對應 owner 審。少數 trivial/hotfix 與無關 CI 失敗有 lead maintainer 例外，不能把例外當一般作者權利。[合併治理][governance]
- 指派後每 2–3 天更新狀態的是 **reviewer**；7 天未 review，可 ping reviewer 或團隊。這是流程期望，不是已量測的回應時間。[review 說明][contributing]
- 有 `action-required` 時，逐項回應：修改或解釋理由；意見不清楚可澄清，僵持時可由 committer 協助。[同上][contributing]
- `gh pr view --comments` 不包含 inline review comments。重新審查前應讀 conversation、reviews、inline comments；需 resolved/outdated 狀態時再讀 GraphQL reviewThreads。[重新審查步驟][checklist]
- 無 write access 的貢獻者，指南列目前最多 6 件 open PR；重要工作被卡住可請 committer 評估 bypass。這是上限，不是建議同時開滿的件數。[PR 限制][contributing]
- stale 工作流程設定：90 天無活動標記，再 30 天關閉；draft PR 與 `keep-open` 豁免。這是排程設定，不保證每筆都在整點到期關閉。[stale 設定][stale]

官方另提供重要貢獻的加速審查聯絡方式，要求說明真實使用情境、問題與修正；本輪只記錄流程，未聯絡任何人。[加速審查方式][contributing]

## 7. 從 Ultralytics 轉過來，要重新校準哪些習慣

| 習慣或規則 | vLLM 的對應做法 |
| --- | --- |
| 以 50 淨新增行、含測試判斷高門檻 | vLLM checklist 的 50／250 行是粗略複雜度指標，可排除測試與文件；不要混算 |
| 新測試預設不加 | vLLM 可重現 bug 要有 before/after 測試證據；仍反對冗餘、瑣碎或高度耦合 mock 的測試 |
| 提醒簽 CLA | vLLM 指南在此明文要求 DCO sign-off；本輪未找到同頁另要求 CLA，不據此推論所有情況都無其他協議 |
| 等推送後自動完整 CI | vLLM 上游 CI 要符合權限並使用指令；pre-commit 另有資格門檻 |
| 依個人習慣省略 AI 標註 | vLLM 明文要求 PR 揭露與 commit attribution |

Ultralytics 對照來自其[固定快照 AGENTS.md][ultralytics-agents]；vLLM 依[指南][contributing]與[checklist][checklist]。最後一列是提醒不要帶入個人習慣，**不是宣稱 Ultralytics 官方禁止 AI 標註**。

## 8. 下一輪最值得補的證據

1. 選幾件小型多模態修正，逐則讀 review 與 inline comments，確認實際要求和指南是否一致。
2. 分開記錄「pre-commit 被擋」「CI 未授權」「測試真失敗」，避免把不同原因混成 CI 失敗率。
3. 在有代表性的樣本量之前，不宣稱新人合併率、回應中位數，或點名 reviewer 能提高合併機率。
4. 真正準備 PR 時再查最新規範、目標分支、重複工作與驗證需求；本輪沒有認領議題。

未做：安裝、build、模型／GPU 測試、實際 CI 指令、Slack 聯絡或上游發文。分支保護、trusted-user 清單與私人治理討論不在本輪可驗證範圍。

## 固定版本來源

[agents]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/AGENTS.md
[contributing]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/contributing/README.md
[checklist]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.agents/skills/pr-checklist/SKILL.md
[template]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.github/PULL_REQUEST_TEMPLATE.md
[dco]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/DCO
[governance]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/governance/process.md
[collaboration]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/governance/collaboration.md
[security]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/SECURITY.md
[precommit]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.github/workflows/pre-commit.yml
[ci-workflow]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.github/workflows/run-ci-command.yml
[ci-script]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.github/workflows/scripts/run_ci_command.py#L534-L591
[stale]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.github/workflows/stale.yml
[ultralytics-agents]: https://github.com/ultralytics/ultralytics/blob/0056e6ce142bac683f712284d6ab135b34193f03/AGENTS.md
