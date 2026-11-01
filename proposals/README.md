# 貢獻提案 / Contribution proposals

本目錄供第一次貢獻 vLLM 的讀者整理提案與證據。每份提案提供繁體中文及英文，兩版的範圍、證據與驗證狀態須一致；正式提交上游只用英文。依 ISO 24495-1 淺白語言原則，先說目的，再交代證據與下一步。

This directory collects proposals and evidence for a first vLLM contribution. Each proposal includes Traditional Chinese and English versions with matching scope, evidence, and validation status. Use only English for upstream submissions. Follow ISO 24495-1 plain-language principles: state the purpose, evidence, and next step.

## 研究分支用途 / Research branch scope

`research/contribution-book` 只保存個人研究，永遠不從這個分支開上游 PR。正式修正須從更新後的 upstream/main 另建乾淨分支，只帶入該題需要的變更。遵守 vLLM 的 [AGENTS.md](../AGENTS.md) 與[貢獻指南](../docs/contributing/README.md)，包含 AI 揭露規則。

`research/contribution-book` stores personal research only. Never open an upstream PR from this branch. Start each contribution from updated upstream/main on a clean branch and include only the relevant changes. Follow vLLM's [AGENTS.md](../AGENTS.md) and [contributing guide](../docs/contributing/README.md), including AI disclosure requirements.

## 提案總表 / Proposal index

尚無可投稿提案。[P01](../research/probe-audit/records/P01.md)已重現 PNG 編碼往返的 EXIF 方向差異；使用場景與預期仍待確認。

No proposal is ready for submission. [P01](../research/probe-audit/records/P01.md) reproduces an EXIF orientation difference after PNG encoding; caller impact and the expected contract still need confirmation.

| 提案 / Proposal | 證據 / Evidence | 狀態 / Status | 下一步 / Next step |
| --- | --- | --- | --- |

參考：[專案選擇調研](../research/oss-candidates/vllm-llamacpp.md)、[教程查核](../research/tutorial-audit/README.md)、[探測式查核](../research/probe-audit/README.md)。

References: [project selection research](../research/oss-candidates/vllm-llamacpp.md), [tutorial audit](../research/tutorial-audit/README.md), and [probe audit](../research/probe-audit/README.md).

如何準備第一筆貢獻，先讀[貢獻研究導讀](../research/contributing/README.md)。本輪僅收集資料，尚未新增提案。

For guidance on a first contribution, start with the [contribution research guide](../research/contributing/README.md). This round gathers evidence; it adds no proposal.
