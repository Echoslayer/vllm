# C01：圖片編碼的 EXIF 方向一致性 / EXIF orientation consistency in image encoding

**狀態：已有局部驗證的實驗補丁，未投稿。** 本卡用於決定工作範圍，不是可直接送出的 PR 說明。

**Status: experimental patch with focused validation; not submitted.** This card defines a possible scope, not a submission-ready PR description.

## 問題與證據 / Problem and evidence

使用者把帶 EXIF 方向的 PIL 圖片交給 `encode_image_url`，再經 connector 與 parser 載入，得到的方向可能不同於直接傳入同一張 PIL 圖片。[P01](../research/probe-audit/records/P01.md)有 24 組方向矩陣；[P02](../research/probe-audit/records/P02.md)以真實同步／非同步 connector 和 parser 重現 6 組方向 6 的寬高差異。固定 vLLM SHA 與環境詳見紀錄。

When a caller passes a PIL image carrying EXIF orientation to `encode_image_url`, decoding through the connector and parser can produce a different orientation from passing the original PIL image directly. P01 records 24 orientation cases; P02 reproduces swapped dimensions in six orientation-6 cases through the real synchronous/asynchronous connector and parser. The records pin the vLLM SHA and environment.

## Mistral 契約補查 / Mistral contract follow-up

[P03](../research/probe-audit/records/P03.md)直接比較 mistral-common 與 vLLM decoder：預轉正後兩者一致，故 #62418 不是此方案必然不相容的證據；但 Mistral 相對原始 bytes 看到的方向會改變。這項語意變更仍需揭露與模型評估，不能把 decoder 一致當成模型行為不變。

P03 directly compares the mistral-common and vLLM decoders. Both agree after pre-normalization, so #62418 does not establish an inherent incompatibility. However, the orientation seen by Mistral changes relative to the original bytes. This semantic change still requires disclosure and model evaluation; decoder agreement does not prove unchanged model behavior.

## 建議範圍 / Suggested scope

先確認 `ImageMediaIO.encode_base64` 應如何保存可見方向，再於其既有 owner 做最小修正，從公開 `encode_image_url` 入口加可失敗的回歸測試。P02 的預先正規化實驗只是支持此方向的證據，不是已審查的補丁。

First establish how `ImageMediaIO.encode_base64` should preserve visible orientation, then make the smallest change at that owner and add a failing regression through the public `encode_image_url` entry point. P02's pre-normalization experiment supports investigating this approach; it is not a reviewed patch.

benchmark `process_image` 的 PIL／bytes 分支有獨立 JPEG 編碼，已另行重現方向差異；修 helper 不會涵蓋它。暫不把此分支與範例自訂 encoder 併入同一修正。

The benchmark `process_image` PIL/bytes branch independently encodes JPEG and reproduces a similar difference. A helper fix would not cover it. Keep that branch and example-specific encoders outside the initial change.

## 實驗進度 / Experiment status

[P04](../research/probe-audit/records/P04.md)保存最新基底上的最小補丁、修改前 6 failed／2 passed，以及修改後 54 passed。已有公開 helper 回歸，但尚未符合 `tests/AGENTS.md` 要求的 LLM／服務入口回歸與模型評估；不是可投稿補丁。

P04 records a minimal patch on an updated base: 6 failed / 2 passed before the fix, and 54 passed across related tests afterward. Public-helper coverage is in place, but the LLM/server regression and model evaluation required for submission remain incomplete.

## 投稿前仍缺什麼 / Before submission

- 確認一般輸入與 Mistral 特定方向政策的邊界，重查 [#62418](https://github.com/vllm-project/vllm/pull/62418)。 / Resolve the general-input versus Mistral-specific orientation policy and recheck #62418.
- 從更新過的 upstream/main 建乾淨分支，完成回歸測試的 red／green 證據與相關既有測試。 / Use a clean branch from updated upstream/main; demonstrate red/green regression coverage and run relevant existing tests.
- 確認真實使用場景，依上游規範補足影響模型輸出時的評估，不把像素探測冒充模型驗證。 / Confirm a real usage scenario and supply model evaluation where required; pixel probes are not model validation.
- 重新完整查重，準備必要文件、DCO 與 AI 揭露，由投稿者逐行理解及審查。 / Repeat duplicate checks, prepare required documentation, DCO and AI disclosure, and have the human submitter understand and review every line.

本輪只保存研究；沒有發 issue、留言或 PR。 / This round only saves research; no issue, comment or PR was posted.
