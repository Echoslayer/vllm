# vLLM 與 llama.cpp 外部貢獻評估

查核日：2026-11-01。原始檔快照：vLLM `5d55ef1590`、llama.cpp `dde879bc4f`。下列 `blob/main`、`blob/master` 連結以此快照為準。

> 公開副本：沿用原調研，未於工作區建立時重新查證；已移除個人設備與帳號權限描述。
> 2026-11-01 貢獻流程研究補充：下文已釐清 vLLM 的 PR 上限適用對象、RFC 門檻與 reviewer 更新責任。其他統計未重算；新查核的規則與驗證限制見[研究導讀](../contributing/README.md)。

## 結論

1. **先投入 vLLM，llama.cpp 排第二。** vLLM 主體約 85% 是 Python，AI 輔助可用，規定是揭露並能自己負責。llama.cpp 主體是 C++，而且禁止用 AI 寫 PR 描述、commit message 和回覆，另有自動檢查。使用者的工作方式是重度 AI 輔助，先走 llama.cpp 風險較高。llama.cpp 第 7 週以後才開始，而且先做手寫重現回報，不先送 code。
2. **起點子系統是 `vllm/multimodal/media/`，加上 `tests/multimodal/`。** 這裡是 Python，處理影像、影片、音訊的讀取與驗證，可用 CPU 測試。外部作者在這個範圍的 PR 合併率 47%（7/15），高於 core 的 17%（15/88）和 kernel/attention 的 25%（28/112）。備案是 [vllm-metal](https://github.com/vllm-project/vllm-metal) 的多模態工作，它只需要 Mac。
3. **第一件 PR 用「自己在 Mac 重現的 bug」，不要搶 good first issue，也不要送純文件 PR。** 條件：能重現、確認無重複、總變更不超過約 100 行、含回歸測試、PR 描述列出修改前後結果、能不靠 AI 口頭解釋每一行。原因是 vLLM good first issue 首次認領的中位數只有 2.3 小時，外部純文件 PR 38 件只合併 1 件。本次沒有找到同時符合「vLLM 主倉、視覺、Mac 可做、無人認領」的現成 issue，所以主線要靠自己找 bug。

最大的流程陷阱：使用者的記憶規則寫「PR 不放 AI 標註、commit 不放 Co-Authored-By」，這條不能帶到這兩個專案。兩邊都要求揭露。vLLM 要在 PR 描述聲明，並加 commit trailer。llama.cpp 要填 PR 模板的 AI 揭露欄；commit 最好自己寫，若由 agent 代 commit，要用 `Assisted-by:`，不是 `Co-authored-by:`。

## 比較表

| 項目 | vLLM | llama.cpp |
| --- | --- | --- |
| 治理 | [PyTorch Foundation 託管](https://pytorch.org/blog/pytorch-foundation-welcomes-vllm/)；[Core Maintainers 即 TSC](https://github.com/vllm-project/vllm/blob/main/docs/governance/process.md) | ggml-org；[ggml.ai 團隊 2026-02 加入 Hugging Face](https://github.com/ggml-org/llama.cpp/discussions/19759)，宣告專案仍社群自主 |
| 授權與簽署 | Apache-2.0；[必須 DCO `Signed-off-by`](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md) | MIT；[CONTRIBUTING](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md) 未提 DCO/CLA |
| AI 政策重點 | 禁純 agent PR；必須揭露；人要審每一行 | 可用 AI 寫 code；禁 AI 寫 PR 描述、commit、回覆；未揭露可永久封鎖 |
| 語言（GitHub bytes） | Python 約 85%，Rust 7%，CUDA 4%，C++ 3%（[API](https://api.github.com/repos/vllm-project/vllm/languages)） | C++ 約 56%，C 16%，Python 7%（[API](https://api.github.com/repos/ggml-org/llama.cpp/languages)） |
| 開放 PR（2026-11-01） | 6,949（`needs-rebase` 3,129、draft 1,603） | 1,838 |
| 月 PR 量（2026-10） | 4,568 | 1,140 |
| PR 上限 | [無 write access 者最多 6 件 open PR](https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/contributing/README.md) | [新手 1 件](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md) |
| 全新外部作者合併率（含未結案） | 26%（55/215） | 30%（88/293） |
| 已結案中的合併率 | 54%（55/101） | 45%（88/195） |
| 首次人類回應中位數 | 23.1 小時 | 11.3 小時 |
| 視覺區全新作者合併 | 13/48（27%） | 1/9（11%） |
| 視覺區 owner | 多人，但負擔不均 | [`llama-mtmd` 只有 ngxson](https://github.com/ggml-org/llama.cpp/blob/master/CODEOWNERS) |
| Mac 可驗證程度 | CPU 測試與 media 邏輯可做，需從原始碼建置；GPU 模型測試不行 | CPU 與 Metal 都可做，但要懂 C++ |
| 主要風險 | 量大、重複工作、PR 長期掛著 | C++ 門檻、AI 文字檢查、單一 owner |

## vLLM

### 治理與社群

- vLLM 於 2025-05 成為 [PyTorch Foundation hosted project](https://pytorch.org/blog/pytorch-foundation-welcomes-vllm/)，由 UC Berkeley 捐贈。
- [process.md](https://github.com/vllm-project/vllm/blob/main/docs/governance/process.md) 列 11 位 Core Maintainers，也就是 Linux Foundation 專案治理中的 TSC；其中 5 位是 Lead Maintainers，負責共識破局與治理變更。
- [committers.md](https://github.com/vllm-project/vllm/blob/main/docs/governance/committers.md) 列 57 位 active committers。[reviewers.md](https://github.com/vllm-project/vllm/blob/main/docs/community/reviewers.md) 列 25 位 reviewers，可核准 PR，但最後由 committer 合併。
- 技術決策在 [Slack 與 GitHub 的 RFC](https://github.com/vllm-project/vllm/blob/main/docs/governance/process.md) 進行。新手入口是 `#pr-reviews`、`#contributors`，另有 `#sig-`、`#feat-` 與每週 contributor sync。
- [Q4 2026 roadmap #61024](https://github.com/vllm-project/vllm/issues/61024) 依 SIG 分段，沒有 Multimodal SIG。它只在 SIG Core 提到 encoder CUDA graph。[process.md](https://github.com/vllm-project/vllm/blob/main/docs/governance/process.md) 說未列入 roadmap 的主題可能得到較少 review。所以選小 bug，不要做大型多模態功能。

### 貢獻規則

[AGENTS.md](https://github.com/vllm-project/vllm/blob/main/AGENTS.md) 原文：

> "Breaching these guidelines can result in automatic banning."
>
> "Pure code-agent PRs are **not allowed**. A human submitter must understand and defend the change end-to-end."
>
> "The submitting human must review every changed line and run relevant tests."

AI 輔助 PR 描述必須包含：

> "Why this is not duplicating an existing PR." / "Test commands run and results." / "Model evaluation results when the change affects output, accuracy, or serving." / "Clear statement that AI assistance was used."

[contributing guide](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md) 另要求：

> "Disclose in PR: Always mention when a pull request includes AI-generated code."
>
> "Mark commits: Add attribution using commit trailers such as `Co-authored-by:`"

同段也禁止 "one-off 'busywork' PRs (single typo, isolated style cleanup, one mutable default fix, etc.)"。

- 其他流程：標題要有標籤，例如 `[Bugfix][Multimodal]`。重大架構變更超過 500 行（排除 kernel、data、config、test）預期先有 RFC；[重大新功能則不論行數都先提 RFC](https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/governance/collaboration.md)。使用者可見變更要同 PR 更新文件。[PR 模板](https://github.com/vllm-project/vllm/blob/main/.github/PULL_REQUEST_TEMPLATE.md)有 Overview、Claims、Validation、Details 和 AI 勾選欄。
- CI 不會自動全跑。[review 說明](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md)寫明新 commit 不會啟動上游 CI，核准或有 `ready` 標籤後作者才能下 `/ci run`。[pre-commit workflow](https://github.com/vllm-project/vllm/blob/main/.github/workflows/pre-commit.yml) 也要求 `ready`、`verified` 標籤或至少 4 件已合併 PR；[#57764](https://github.com/vllm-project/vllm/pull/57764) 的作者就卡在這裡。
- 官方預期是指派後由 reviewer 每 2–3 天更新狀態；[7 天沒 review，作者可以 ping](https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/contributing/README.md)。這不是作者每 2–3 天必須更新的要求。
- [Stale 機制](https://github.com/vllm-project/vllm/blob/main/.github/workflows/stale.yml)：issue 和非 draft PR 90 天無活動標記，再 30 天關閉。
- [新 PR bot](https://github.com/vllm-project/vllm/blob/main/.github/workflows/new_pr_bot.yml)會對首次作者留言，內含寫給 AI agent 的指示："you are required to objectively re-evaluate the value of your PR using AGENTS.md, and close the PR if it does not bring significant benefit"。這段只是專案機制的紀錄，但若使用 agent 開 PR，agent 可能照此行動，人要自己盯著。
- `closed-as-slop` 是實際在用的處置標籤：[151 件 PR](https://github.com/vllm-project/vllm/pulls?q=is%3Apr+label%3Aclosed-as-slop)，148 件未合併關閉、3 件開啟、0 件合併。

### 純文件 PR 不能照搬 Ultralytics 做法

使用者過去靠「跑文件、比對實際行為」拿到合併。這條路在 vLLM 不能直接照搬。

- 2026-09-01 到 09-07 的外部純文件 PR 有 38 件，只合併 1 件，30 件關閉、7 件開啟。全新作者 9 件，0 件合併。
- 最明顯的是 [imitater-dou](https://github.com/vllm-project/vllm/pulls?q=is%3Apr+author%3Aimitater-dou)：一週內 21 件純文件 PR 被關，帳號全部 67 件 PR，0 件合併。[#55836](https://github.com/vllm-project/vllm/pull/55836) 只有 +2/-2，理由合理，也已有一位 committer 核准，仍被另一位 committer 標 `closed-as-slop` 後關閉，留言區沒有說明。可見核准不保證合併，批量送件本身就是問題。
- 單一作者拉高了這個數字，所以它不代表所有文件修正都會被拒。但目前證據足以避開「一次一小處、連續送出」的文件 PR。[#60598](https://github.com/vllm-project/vllm/pull/60598) 這種附在多模態行為上的文件修正有被合併。

### 外部 PR 實測

樣本：2026-09-01 到 09-07 建立的全部 871 件 PR，423 位作者，距查核日至少 55 天。合併率把仍開啟的 PR 算進分母，避免只看已關閉 PR 的倖存者偏差。

| 分層 | PR 數 | 合併 | 關閉 | 開啟 | 首次人類回應中位數 | 無人類回應 | 合併耗時中位數 | 合併 PR 中位變更行數 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 核心成員 | 192 | 76% | 12% | 12% | 12.0h | 17% | 25.1h | 69 |
| 常客（先前已合併 5 件以上） | 129 | 50% | 24% | 26% | 17.5h | 26% | 78.9h | 90 |
| 有公司訊號的新面孔 | 283 | 27% | 33% | 40% | 40.0h | 48% | 224.8h | 149 |
| 無公司訊號，先前 1-4 件 | 49 | 35% | 22% | 43% | 4.5h | 37% | 23.7h | 98 |
| 全新作者（先前 0 件、無公司訊號） | 215 | 26% | 21% | 53% | 23.1h | 38% | 169.2h | 88 |

- 全新作者：150 人，其中 44 人（29%）在樣本內至少合併一件。
- 全新作者依大小的合併率：20 行以下 30%，20-99 行 30%，100-499 行 24%，500 行以上 16%。
- 有公司訊號一層排除 imitater-dou 後是 77/254（30%）。
- 外部作者的關閉原因（149 件）：作者自關 98、`closed-as-slop` 32、維護者關閉 14、未知 5。
- 維護者關閉的 14 件逐則讀過：9 件是併入他人 PR、重複、已被修掉或被取代，3 件是前提不成立或功能將移除，1 件太大（[#54654](https://github.com/vllm-project/vllm/pull/54654)），1 件無留言。其中 [#55765](https://github.com/vllm-project/vllm/pull/55765) 維護者重做修正並把原作者列為 coauthor。
- 所以「關閉」不等於工作被否定，但也拿不到一件自己的合併。

### Merged 與 closed 是否反映實際結果

- 樣本中 206 件關閉未合併 PR，編號都沒有以 `(#N)` 出現在 main 的 commit 標題上。
- 359 件 merged 有 358 件能在 main 找到；例外是 [#55760](https://github.com/vllm-project/vllm/pull/55760)。
- 因此 GitHub 狀態對「該 PR 是否落地」基本可靠。它不能判斷的是「修正是否經由別的 PR 落地」，前述 9 件就是這種。

### 誰審哪裡，負擔多重

- [CODEOWNERS](https://github.com/vllm-project/vllm/blob/main/.github/CODEOWNERS)：`/vllm/multimodal` 是 DarkLight1337、ywang96、NickLucche、tjtanaa、shen-shanshan；`/vllm/multimodal/media` 是 Isotr0py；`/tests/models` 含 DarkLight1337、ywang96、AndreasKaratzas。
- [committers.md](https://github.com/vllm-project/vllm/blob/main/docs/governance/committers.md) 的 Multi-modal Input Processing owner 是 DarkLight1337、ywang96、Isotr0py。
- 2026-08-03 以來，標題含 Multimodal 且合併的 137 件中，DarkLight1337 合併 45 件，Isotr0py 28 件，兩人佔 53%。

| 帳號 | 開放 review request | 10 月有 review 且有更新的 PR |
| --- | ---: | ---: |
| DarkLight1337 | 933 | 260 |
| ywang96 | 959 | 23 |
| NickLucche | 855 | 76 |
| tjtanaa | 550 | 112 |
| shen-shanshan | 143 | 50 |
| Isotr0py | 83 | 200 |

開放 review request 含大量舊請求，不能當成真實待辦量。實際訊號是 DarkLight1337 和 Isotr0py 很活躍，而且小型 bug fix 可很快合併。[#64032](https://github.com/vllm-project/vllm/pull/64032) 0.1 天、[#53744](https://github.com/vllm-project/vllm/pull/53744) 0.1 天。

### 多模態區的新手案例

2026-08 以來，100 件非核心作者的 Multimodal 標題合併 PR 中，有 38 件來自先前 0 件合併的作者。這 38 件含公司員工。適合使用者模仿的是這幾件：

| PR | 規模 | 所需能力 |
| --- | ---: | --- |
| [#62704](https://github.com/vllm-project/vllm/pull/62704) 損壞 PNG 回 400 | +19/-1 | 讀 Pillow 例外、改 `image.py`、補測試 |
| [#61986](https://github.com/vllm-project/vllm/pull/61986) RGB PNG 透明度 | +102/-16 | 影像格式知識、對照既有 RGBA 行為 |
| [#64032](https://github.com/vllm-project/vllm/pull/64032) 本地媒體停用時回 400 | +34/-3 | 追 connector 例外；驗證寫明在 macOS arm64 CPU build |
| [#53744](https://github.com/vllm-project/vllm/pull/53744) base64 音訊錯誤回 400 | +13/-1 | 輸入驗證 |
| [#59399](https://github.com/vllm-project/vllm/pull/59399) 處理器參數優先序測試 | +37/-0 | 只補處理器參數測試 |
| [#62497](https://github.com/vllm-project/vllm/pull/62497) `mm-processor` E2E 測試 | +82/-0 | CLI 測試 |

這些 PR 不需要 C++、CUDA 或 kernel 知識。影像格式經驗剛好是使用者的優勢。

### 入門資源品質

- 開放的 [good first issue](https://github.com/vllm-project/vllm/issues?q=is%3Aissue+state%3Aopen+label%3A%22good+first+issue%22) 有 17 件，13 件已有 assignee。
- 2026 年建立的 31 件 good first issue：首次認領中位數 2.3 小時，四分之一在 0.2 小時內，平均被 6.1 件 PR 引用。
- [看板 6](https://github.com/orgs/vllm-project/projects/6)「Onboarding Tasks」只剩 2 張 2025-03 的 draft 卡，都是效能基準任務，無 assignee，沒有實際入門價值。
- [看板 10](https://github.com/orgs/vllm-project/projects/10)「Multi-modal Model Requests」共 83 項：Todo 8、Abandoned 4、In Progress 0、Done 71。8 件 Todo 中 6 件已關閉；開啟的 [#28509](https://github.com/vllm-project/vllm/issues/28509) 和 [#23943](https://github.com/vllm-project/vllm/issues/23943) 都是語音模型。
- 兩個看板都不能當入口。

### 開發與硬體

- [Python 開發可用預編譯安裝](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md)，但 [Apple Silicon 沒有預建 CPU wheel](https://github.com/vllm-project/vllm/blob/main/docs/getting_started/installation/cpu.apple.inc.md)，要從原始碼建置，官方標為實驗性支援。
- [macOS CI 排程](https://github.com/vllm-project/vllm/blob/main/.github/workflows/macos-smoke-test.yml)每天一次，不是每 PR。[2026-11-01 成功 run](https://github.com/vllm-project/vllm/actions/runs/41265494634) 的安裝加建置：macos-15 約 5 分鐘，macos-26 約 8.6 分鐘，這是 GitHub runner 含快取的數字。
- CI 有 [CPU 的 Multimodal Processor 分片](https://github.com/vllm-project/vllm/blob/main/.buildkite/test_areas/models_multimodal.yaml)，也有 [`pytest -m cpu_test multimodal`](https://github.com/vllm-project/vllm/blob/main/.buildkite/test_areas/misc.yaml)。生成測試跑在 H200 或 AMD GPU。
- [官方警告](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md)不是所有單元測試都能在 CPU 通過，沒有 GPU 時要依賴 CI。
- `vllm/multimodal/media/` 共 6 個 Python 檔，`tests/multimodal/media/` 有對應測試。[#64882](https://github.com/vllm-project/vllm/issues/64882) 的回報者就是在 M4 16GB 上用 CPU backend 重現多模態 bug，並開了 [#64899](https://github.com/vllm-project/vllm/pull/64899)。
- 影響模型輸出的改動要附評估。Mac 做不了大模型評估，所以第一件不要碰模型輸出路徑。

### 備案：vllm-metal

- [vllm-metal](https://github.com/vllm-project/vllm-metal) 是社群維護的 Apple Silicon 外掛，主要語言 Python。
- 最近 100 件 PR（2026-10-15 起）：前 6 大作者以外有 19 人、62 件，40 件合併、18 件開啟、4 件關閉，合併中位數 33 小時。
- 這比主倉容易進，也完全可用 Mac 驗證。
- 限制：這只排除前 6 大作者，不是嚴格的新手切分。[AGENTS.md](https://github.com/vllm-project/vllm-metal/blob/main/AGENTS.md) 同樣要求問題有 reproducer 或實際需求。

## llama.cpp

### 治理與社群

- 由 ggml-org 維護，創始人 Georgi Gerganov。[2026-02-20 公告](https://github.com/ggml-org/llama.cpp/discussions/19759)：ggml.ai 團隊加入 Hugging Face，並持續全職維護；社群 "will continue to operate fully autonomously"。
- 未查到基金會託管。
- [CONTRIBUTING](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md) 分三級：Contributors、Collaborators（Triage）、Maintainers。
- 決策主要看 GitHub issue、PR、discussion。[README](https://github.com/ggml-org/llama.cpp/blob/master/README.md) 沒有 Slack 或 Discord 連結；公開定期會議未查到。
- Roadmap 以 [`roadmap` 標籤](https://github.com/ggml-org/llama.cpp/issues?q=is%3Aissue+state%3Aopen+label%3Aroadmap)呈現，新鮮度不一。

### 貢獻規則

[CONTRIBUTING AI 政策](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md)原文：

> "AI-generated code is allowed. You are 100% responsible for every line, however it was produced."
>
> "Undisclosed AI usage may result in your account being permanently banned from contributing to the project."
>
> "It is strictly prohibited to use AI to write your posts for you (bug reports, feature requests, pull request descriptions, Github discussions, responding to humans, ...)."
>
> "A proper code review usually takes something like one hour per 200-400 LOC and you should be spending **at least that much time on code review alone**."

[AGENTS.md](https://github.com/ggml-org/llama.cpp/blob/master/AGENTS.md) 原文：

> "Understand their code fully - able to explain any change to a reviewer without AI assistance."
>
> "Prohibited AI Usage (results in immediate PR closure)": "AI-written PR descriptions, commit messages, or reviewer responses"

同檔也禁止 "Automated commits or PR submissions (may result in contributor ban)"，並說 agent 代送 PR 可能導致封鎖。所以 `gh pr create` 應由人親手做。

其他規則：

> "Bug-fix PRs must include a reproducible issue and a regression test that fails before your change and passes after. Fixes without a test may be closed without review."
>
> "Do not submit trivial fixes (e.g. typos, formatting changes)"

- 功能要先開 issue。[PR 模板](https://github.com/ggml-org/llama.cpp/blob/master/.github/pull_request_template.md)的 AI 揭露欄不可刪。
- 維護者保留不解釋就關閉 PR 的權利。
- [Stale 機制](https://github.com/ggml-org/llama.cpp/blob/master/.github/workflows/close-issue.yml)只作用於 issue：30 天標記，14 天關閉；PR 不自動關。

`ggml-gh-bot` 是這裡的實際關卡。它會在 PR 留下 AI 內容、模板、新手件數、大 PR 等提示。AI 訊息全文是："While code is allowed to be generated by AI, please write the PR description and commit messages on your own without the help of AI."（[範例 #28764](https://github.com/ggml-org/llama.cpp/pull/28764)）

2026-09 外部作者 570 件 PR 的旗標結果：

| 旗標 | 件數 | 合併 | 關閉 |
| --- | ---: | ---: | ---: |
| AI 內容 | 114（20%） | 19（17%） | 54 |
| 模板未遵守 | 198 | 27（14%） | 91 |
| 新手超過 1 件 | 97 | 23（24%） | 39 |
| 大 PR | 30 | 3（10%） | 14 |
| 前 6 則留言內無旗標 | 262 | 125（48%） | 60 |

這是相關性，不是因果；旗標可重疊。維護者也會直接引用政策關 PR，例如 [#28358](https://github.com/ggml-org/llama.cpp/pull/28358)、[#28871](https://github.com/ggml-org/llama.cpp/pull/28871)、[#29763](https://github.com/ggml-org/llama.cpp/pull/29763)。

### 外部 PR 實測

樣本：2026-09-01 到 09-30 建立的全部 1,050 件 PR，463 位作者，距查核日至少 32 天。

| 分層 | PR 數 | 合併 | 關閉 | 開啟 | 首次人類回應中位數 | 無人類回應 | 合併耗時中位數 | 合併 PR 中位變更行數 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 核心成員 | 414 | 83% | 9% | 8% | 2.1h | 16% | 16.3h | 30 |
| 常客 | 65 | 72% | 20% | 8% | 8.9h | 12% | 19.7h | 79 |
| 有公司訊號的新面孔 | 236 | 39% | 27% | 35% | 7.1h | 33% | 84.4h | 31 |
| 無公司訊號，先前 1-4 件 | 41 | 37% | 34% | 29% | 14.4h | 29% | 112.2h | 48 |
| 全新作者 | 293 | 30% | 37% | 33% | 11.3h | 37% | 95.1h | 26 |

- 全新作者 207 人，其中 63 人（30%）至少合併一件。
- 依大小的合併率：20 行以下 40%，20-99 行 30%，100-499 行 18%，500 行以上 22%。
- 外部作者關閉 184 件：作者自關 125、維護者關閉 57、未知 2。
- 維護者關閉的 57 件人工分類：AI 政策或 AI 內容疑慮 12、重複或被取代 13、修法或設計不被接受 15、無留言 15、其他 2。
- 維護者評語直接，例如 [#28664](https://github.com/ggml-org/llama.cpp/pull/28664) "not a real fix"、[#28922](https://github.com/ggml-org/llama.cpp/pull/28922) "not worth the opportunity cost to review"。
- 自關 PR 中位數只有 15.7 小時，66 件在 24 小時內；17 件同作者有相似標題 PR，6 件其後合併。抽讀 8 件，常見原因是被其他變更取代，也有不留言的情況。
- 237 件關閉未合併 PR 都沒有以 `(#N)` 出現在 master commit 標題上。583 件 merged 有 578 件能對上；未對上的 5 件含 3 件 `sync : ggml`。狀態同樣基本可靠。

### mtmd 與 reviewer

- [CODEOWNERS](https://github.com/ggml-org/llama.cpp/blob/master/CODEOWNERS)：`/tools/mtmd/` 歸 `llama-mtmd`，該組只有 ngxson。`/conversion/` 歸 CISC，`/src/models/` 歸 `llama-models`。
- 2026-07-15 以來（最早一筆 07-28）標題含 mtmd 且合併的 67 件中，ngxson 合併 64 件、自己寫 35 件。
- ngxson 開放 review request 409，10 月有 review 且有更新的 PR 123 件，同月自己開 35 件 PR。
- 2026-09 樣本中，動到 `tools/mtmd/` 的全新作者 PR 9 件，只有 [#28919](https://github.com/ggml-org/llama.cpp/pull/28919) 合併，耗時 884 小時；6 件沒有人類回應，第一次回應中位數 45.3 小時。
- 成功案例多半是模型或視覺邏輯：[#27057](https://github.com/ggml-org/llama.cpp/pull/27057) +119/-2 修 LFM2 tiling、[#26653](https://github.com/ggml-org/llama.cpp/pull/26653) +205/-65 修 Granite4 圖序、[#25781](https://github.com/ggml-org/llama.cpp/pull/25781) +1/-1 修 position embedding 內插、[#26536](https://github.com/ggml-org/llama.cpp/pull/26536) +2/-4 修音訊 chunk。這些需要讀 C++、看 ggml 圖、與 HF 原實作對照。
- 2026-07-15 以來，非 CODEOWNERS 作者先前 0 件合併的 mtmd 標題 PR 有 9 件（含公司員工）。
- 反例是輸入驗證類 PR 會卡住：[#26237](https://github.com/ggml-org/llama.cpp/pull/26237) +7/-0 自 7 月開啟仍未合併，[#27202](https://github.com/ggml-org/llama.cpp/pull/27202) 自 8 月開啟仍未合併。ngxson 自己的 [#29276](https://github.com/ggml-org/llama.cpp/pull/29276) 當天合併。

### 入門資源品質

- [good first issue](https://github.com/ggml-org/llama.cpp/issues?q=is%3Aissue+state%3Aopen+label%3A%22good+first+issue%22) 開放 16 件，0 件有 assignee，最舊來自 2023，品質參差。
- 2025-07 以來建立的 19 件，有認領訊號的 18 件，首次認領中位數 142 小時，遠比 vLLM 慢。
- 沒有專門的 onboarding 看板。

### 開發與硬體

- [build-apple](https://github.com/ggml-org/llama.cpp/blob/master/.github/workflows/build-apple.yml) 的 [成功 run](https://github.com/ggml-org/llama.cpp/actions/runs/41282181429) 建置約 1 分 17 秒、測試約 1 分 32 秒。這是有 ccache 的 CI 數字，不是冷建置。
- [tests/CMakeLists.txt](https://github.com/ggml-org/llama.cpp/blob/master/tests/CMakeLists.txt) 有 `test-mtmd-c-api`、`test-mtmd-impl`。
- [`tools/mtmd/tests.sh`](https://github.com/ggml-org/llama.cpp/blob/master/tools/mtmd/tests.sh) 用實際模型測試，並分 big、huge 模式。
- [CONTRIBUTING](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md) 說新模型先做 CPU，並要求發布前在本機執行 [完整 CI](https://github.com/ggml-org/llama.cpp/blob/master/ci/README.md)。
- Mac 足以做 CPU 與 Metal 驗證。難點是 C++ 能力，不是硬體。[clip.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/mtmd/clip.cpp) 約 381KB，[mtmd.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/mtmd/mtmd.cpp) 約 161KB。

## 第一件 PR 候選

### 選擇規則

1. 先在 Mac 重現，留下修改前輸出。
2. 依 [vLLM 重複檢查指令](https://github.com/vllm-project/vllm/blob/main/AGENTS.md)查 issue 和 open PR。
3. 不碰模型輸出路徑、scheduler、kernel。
4. 總變更約 100 行內，含失敗後通過的測試。
5. 使用者關掉 AI 後，能講清楚根因、為何這樣修、測試擋住什麼。做不到就不送。

### 候選

| 順位 | 候選 | 無人認領的證據 | 適合原因 | 主要風險 |
| --- | --- | --- | --- | --- |
| 1 | vLLM 自找 bug：[`image.py`](https://github.com/vllm-project/vllm/blob/main/vllm/multimodal/media/image.py)、[`video.py`](https://github.com/vllm-project/vllm/blob/main/vllm/multimodal/media/video.py) 與 HF 或 Pillow 行為對照 | 尚未存在 issue；要送前依規則確認 | 最接近影像 AI 專長，CPU 可驗證；先例 [#62704](https://github.com/vllm-project/vllm/pull/62704)、[#61986](https://github.com/vllm-project/vllm/pull/61986) | 近期已有多件類似修補，例如 [AVIF/BLP #63433](https://github.com/vllm-project/vllm/pull/63433)；若只是再加一種例外，可能被視為低價值 |
| 2 | vLLM [#47788](https://github.com/vllm-project/vllm/issues/47788) 第 1 部分：`use_audio_in_video` 啟動時 dummy 輸入崩潰 | 無 PR 引用、無 assignee；回報者 7 月說可送 PR，但沒有送 | 問題在 Python 處理器與 dummy 輸入層，根因已寫明 | 2026-10-06 標 stale，約 11-05 自動關閉；回報者可能回來；音訊而非影像；Mac 重現未驗證；要先在 issue 問，並只做第 1 部分 |
| 3 | vllm-metal [Roadmap #1005](https://github.com/vllm-project/vllm-metal/issues/1005) 的「Support multimodal LFM input on PyTorch MPS」 | [LFM 搜尋](https://github.com/vllm-project/vllm-metal/pulls?q=is%3Apr+LFM)只見文字 MPS [#880](https://github.com/vllm-project/vllm-metal/pull/880) 與 MLX 影像 [#1182](https://github.com/vllm-project/vllm-metal/pull/1182)，未見 MPS 多模態 PR | 只需要 Mac，視覺模型，Python 為主 | 範圍可能超過 100 行；MPS 問題較難除錯；Roadmap 留言未全部讀完，動手前要先留言確認 |
| 4 | llama.cpp [#29780](https://github.com/ggml-org/llama.cpp/issues/29780)：Granite4 Vision `window_side=0` 除以零 | 0 留言、無 PR 引用；程式碼仍是[讀值無檢查](https://github.com/ggml-org/llama.cpp/blob/dde879bc4f/tools/mtmd/clip.cpp#L2381)後[直接除](https://github.com/ggml-org/llama.cpp/blob/dde879bc4f/tools/mtmd/clip.cpp#L5045) | 改動小，issue 附重現法，macOS 可重現 | 要 C++ 與回歸測試；11-01 已標 stale，約 11-15 自動關閉；同類驗證 PR 卡住；只有 ngxson 能審；描述要全手寫 |
| 5 | llama.cpp [#30195](https://github.com/ggml-org/llama.cpp/issues/30195)：EmbeddingGemma-2 影像 token 超過設定 | 0 留言、無 PR 引用 | 回報在 CPU，適合「跑出結果再比對」，先交手寫重現報告即可 | 可能是設定或模型匯出問題，不一定有 code fix；標 `bug-unconfirmed`，不在 stale 豁免標籤內，無活動會被自動關閉 |

### 看似可做但已被佔

- [#64882](https://github.com/vllm-project/vllm/issues/64882) 有 [#64899](https://github.com/vllm-project/vllm/pull/64899)。
- [#64202](https://github.com/vllm-project/vllm/issues/64202) 有 [#64201](https://github.com/vllm-project/vllm/pull/64201)。
- [#64541](https://github.com/vllm-project/vllm/issues/64541) 有 [#64543](https://github.com/vllm-project/vllm/pull/64543)，而且要 TP 2。
- [#55546](https://github.com/vllm-project/vllm/issues/55546) 有 [#63790](https://github.com/vllm-project/vllm/pull/63790)。
- [#47860](https://github.com/vllm-project/vllm/issues/47860) 有 [#49682](https://github.com/vllm-project/vllm/pull/49682)、[#50875](https://github.com/vllm-project/vllm/pull/50875)。
- [#57671](https://github.com/vllm-project/vllm/issues/57671) 維護者說要併 [#48354](https://github.com/vllm-project/vllm/pull/48354)。
- [#38425](https://github.com/vllm-project/vllm/issues/38425) 依賴 Transformers [PR #47047](https://github.com/huggingface/transformers/pull/47047)，已有人等著做 vLLM 端。
- llama.cpp [#30508](https://github.com/ggml-org/llama.cpp/issues/30508) 已有 [#30510](https://github.com/ggml-org/llama.cpp/pull/30510)，模型團隊也說會處理。

## 8 週計畫與停損

假設每週 6-8 小時業餘時間。這是規劃假設，不是查證事實。目標是 1 件合併和 1 件有實質 review 的第二件 PR，不追求 Ultralytics 的件數。

| 週 | 工作 | 完成標準 |
| --- | --- | --- |
| 1 | 確認公司對個人開源與 DCO 的規定；在 Mac 從原始碼裝 vLLM；跑 `tests/multimodal/media` 的 CPU 測試；加入 Slack | 有測試基線，知道哪些在 Mac 必敗 |
| 2 | 手讀 `media/`、測試與 6 件先例 PR；不用 AI，寫一頁資料流筆記 | 能講出請求如何變成影像 tensor，以及錯誤如何變 400 |
| 3 | 用格式邊界和 HF/Pillow 對照找 bug；若 #47788 仍活著，先手動問 | 至少 1 個可重現問題，或確定改走候選 3 |
| 4 | 開 issue，再開第一件 PR；執行 `pr-checklist`；揭露 AI，commit 加 `Signed-off-by` 和 trailer | PR 含 Validation，無重複 |
| 5-6 | 回應 review；7 天無回應再 ping，或到 `#pr-reviews` 問一次；每次改動都自己讀 | 回覆內容能自行解釋，不貼 AI 長文 |
| 7 | 第二件同區 PR，或 vllm-metal 備案；同時在 llama.cpp 選候選 5，手寫重現報告 | llama.cpp 階段不送 code |
| 8 | 結算：合併數、被改幾輪、哪些 AI 建議錯了 | 決定續做、轉 metal 或停止 |

### 第 8 週現實預期

- 依樣本，單件 PR 的合併機率大約四分之一到一半。
- 全新作者合併中位數約 7 天，p75 約 21 天，而且只算有合併的 PR。
- 以使用者目前軟體基礎，寫 CUDA、kernel、新模型支援都不切實際，不要試。
- 使用者的優勢是影像格式、模型輸入和實測比對，不是系統程式設計。

### 停損條件

- 任一 PR 被標 `closed-as-slop`，或收到 `ggml-gh-bot` 的 AI 內容提示：立刻暫停新 PR，先檢討。
- 第 4 週結束還不能不靠 AI 解釋自己的改動：不送 vLLM 主倉，改 vllm-metal 或停止。
- 第 8 週累計 2 件 vLLM 主倉 PR 都沒有合併，且其中至少 1 件在依程序 ping 後 14 天仍無人類回應：停止主倉投入，只留 vllm-metal。
- 一件 PR 重工超過 3 輪仍被質疑根因：放棄該件。
- 第 7 週前不要用 llama.cpp 當主線。若任何 llama.cpp 文字需要 AI 代寫才能完成，就不要送。
- 只使用已獲授權的設備；Mac 無法完成的驗證就不接該任務。

## 未查證事項

- **Mac 實測**：本次沒有在使用者 Mac 建置或跑測試。可測試範圍只來自 CI 設定、官方文件和回報者環境。冷建置時間也未量。
- **公司可否貢獻**：適用的開源貢獻與智財規定未查，需要貢獻者自行確認。
- **公司員工分層**：只靠 GitHub company 欄位、作者 email 網域和先前合併數。vLLM 有公司訊號的 283 件中 95 件 company 欄為空；學校可能被誤判，全新作者層也還混有員工，例如 [am-cohere](https://github.com/vllm-project/vllm/pull/54774)。分層結果應視為近似。
- **人類回應定義**：包含非維護者留言，只掃前 10 則 review 和前 15 則留言。部分帳號可能是自動化使用者，但未被標為 Bot。
- **`ggml-gh-bot`**：判定邏輯與準確率未查到。合併率差異不代表因果。
- **AI 揭露與合併率**：全新作者中，vLLM 揭露組 8/70、未揭露組 47/145；llama.cpp 兩組都是 30%。分類靠正規表示式，且受 PR 類型影響，不可解讀為「揭露會降低合併」。
- **先前發現中的 28/45 與 23/31**：當時的分組定義不明，無法重現。本次只排除 committer、reviewer 和 CODEOWNERS 帳號，最近 100 件已關閉 PR 中 vLLM 非核心 42/60、llama.cpp 33/43。已關閉樣本本身有倖存者偏差。
- **先前發現中的 6,941**：現在是 6,949。
- **永久封鎖案例**：規則條文已確認，但未確認近期實際封鎖案例。
- **Slack 與會議**：未加入 Slack，未讀 standup 筆記與 SIG 會議紀錄。`roadmap.vllm.ai`、`standup.vllm.ai` 未開啟。
- **看板 10**：Done 只讀到 71 件中的前 25 件。看板內容來自公開頁面 HTML；未使用 Projects API。
- **pytorch.org/projects**：頁面內容是 iframe，無法直接讀到專案清單；託管身分依官方部落格確認。
- **#47788 Mac 重現可行性、#29780 實際重現、LFM MPS 工作量**：都只讀文字和程式碼，未執行。
- **樣本窗不等長**：vLLM 只取 7 天，llama.cpp 取 30 天，且長度不同的觀察期會影響開啟比例，兩邊只能粗略比較。

## 來源

### vLLM

- [AGENTS.md](https://github.com/vllm-project/vllm/blob/main/AGENTS.md)
- [Contributing](https://github.com/vllm-project/vllm/blob/main/docs/contributing/README.md)
- [Governance process](https://github.com/vllm-project/vllm/blob/main/docs/governance/process.md)
- [Committers](https://github.com/vllm-project/vllm/blob/main/docs/governance/committers.md)
- [Reviewers](https://github.com/vllm-project/vllm/blob/main/docs/community/reviewers.md)
- [CODEOWNERS](https://github.com/vllm-project/vllm/blob/main/.github/CODEOWNERS)
- [PR template](https://github.com/vllm-project/vllm/blob/main/.github/PULL_REQUEST_TEMPLATE.md)
- [Stale workflow](https://github.com/vllm-project/vllm/blob/main/.github/workflows/stale.yml)
- [New PR bot](https://github.com/vllm-project/vllm/blob/main/.github/workflows/new_pr_bot.yml)
- [Pre-commit workflow](https://github.com/vllm-project/vllm/blob/main/.github/workflows/pre-commit.yml)
- [模型測試文件](https://github.com/vllm-project/vllm/blob/main/docs/contributing/model/tests.md)
- [PyTorch Foundation 公告](https://pytorch.org/blog/pytorch-foundation-welcomes-vllm/)

### llama.cpp

- [CONTRIBUTING.md](https://github.com/ggml-org/llama.cpp/blob/master/CONTRIBUTING.md)
- [AGENTS.md](https://github.com/ggml-org/llama.cpp/blob/master/AGENTS.md)
- [CODEOWNERS](https://github.com/ggml-org/llama.cpp/blob/master/CODEOWNERS)
- [PR template](https://github.com/ggml-org/llama.cpp/blob/master/.github/pull_request_template.md)
- [mtmd README-dev](https://github.com/ggml-org/llama.cpp/blob/master/tools/mtmd/README-dev.md)
- [Hugging Face 公告 discussion](https://github.com/ggml-org/llama.cpp/discussions/19759)

### 實測方法

- 資料以 GitHub GraphQL 與 REST 唯讀取得，取樣日 2026-11-01；vLLM 查詢為 `repo:vllm-project/vllm is:pr created:2026-09-01..2026-09-07`，llama.cpp 查詢為 `repo:ggml-org/llama.cpp is:pr created:2026-09-01..2026-09-30`。
- 核心成員：vLLM 取 committers、reviewers、CODEOWNERS、作者關聯為 MEMBER/OWNER；llama.cpp 取 CODEOWNERS、公開 org 成員、MEMBER/OWNER。
- 常客：先前已合併至少 5 件。公司訊號：company 欄或非免費、非學校 email 網域。全新作者：2026-09-01 前該倉 0 件合併且無公司訊號。
- 首次人類回應：排除 Bot 與作者本人；中位數只算非 draft 且有回應者。
- 視覺區：vLLM 為 `vllm/multimodal/`、`tests/multimodal/`、`tests/models/multimodal/`、`vllm/model_executor/models/`、`vllm/models/`、`docs/features/multimodal`；llama.cpp 為 `tools/mtmd/`。每件 PR 只掃前 15 個檔案。
- 看 review request 用 `review-requested:<login>`，看 10 月活動用 `reviewed-by:<login> updated:2026-10-01..2026-10-31`。後者是近似值。
