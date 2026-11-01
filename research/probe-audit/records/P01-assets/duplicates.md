# P01 查重：EXIF 方向與透明圖片的 base64 編碼

查核日期：2026-11-01，UTC 12:45–12:48。僅查公開資料，未發 issue、PR 或留言。

**在本輪搜尋與已讀 patch 中，尚未找到直接修正「RGBA／LA 圖片在 `encode_image_base64` 轉 RGB 時失去 EXIF 方向資訊」的 PR。** 這是起始查重假設；查詢同時包含一般 EXIF 與編碼關鍵詞，沒有全部限縮到 RGBA。主探測後續若擴及 RGB，仍需依最終確認的 API 契約重查。這不等於證明沒有重複，也不表示待查現象已是產品 bug。下面三件開啟中的 PR 涉及相同載入模組，正式提案前應重查它們的最新 head。

## 搜尋方法與結果

使用 GitHub REST `GET /search/issues`，每次加 `repo:vllm-project/vllm`，同時涵蓋 open／closed issues 與 PR；`per_page=100`。各結果均少於 100，`incomplete_results=false`，沒有因頁數上限截斷。API 擷取檔暫存於本次 scratch 目錄，沒有提交全文到研究書。

| 完整查詢（共同前綴 `repo:vllm-project/vllm`） | 件數 |
| --- | ---: |
| `EXIF` | 17 |
| `encode_image_base64` | 14 |
| `rgba_to_rgb` | 3 |
| `orientation transparency` | 5 |
| `EXIF RGBA` | 5 |
| `EXIF LA` | 1 |
| `encode_base64 EXIF` | 0 |
| `EXIF base64` | 6 |
| `orientation encode` | 7 |
| `orientation RGBA` | 5 |

查詢有重疊，不能把件數相加當成獨立議題數。最初 `gh search issues` 的整句參數被 CLI 解成錯誤 repo qualifier；該次失敗不算搜尋結果，後續全部改用上面的 REST 查詢完成。

## 已讀的相關 PR

| PR／查核時狀態 | 已確認處理的範圍 | 與 P01 的關係 |
| --- | --- | --- |
| [#44974](https://github.com/vllm-project/vllm/pull/44974)，2026-06-09 已合併 | `load_bytes` 在開檔後套用 EXIF transpose；共用轉色支援 tRNS 透明度 | 是方向與透明處理的歷史來源；已讀 patch 沒有修改 `encode_base64` |
| [#47566](https://github.com/vllm-project/vllm/pull/47566)，2026-07-03 已合併 | parser 對直接傳入的 PIL image 先 normalize 再轉 RGB，使其與 bytes loader 一致 | 是離線／載入路徑的一致性先例；沒有修改編碼入口 |
| [#61986](https://github.com/vllm-project/vllm/pull/61986)，2026-10-16 已合併 | RGB PNG tRNS 不再被 same-mode early return 略過；共用透明轉色 | 上一輪已讀完整 diff；處理透明色與線上／離線一致性，未針對 encode 時 EXIF metadata 流失 |
| [#62418](https://github.com/vllm-project/vllm/pull/62418)，open | Mistral tokenizer 路徑停用 EXIF normalization，讓 vLLM decode 與 `mistral_common` 一致 | 不是編碼修正；但會改 `load_bytes` 和直接 PIL 輸入的方向政策，可能影響 P01 的參考行為 |
| [#63369](https://github.com/vllm-project/vllm/pull/63369)，open | 新增 TorchCodec 解碼 backend；透明圖片保留 Pillow fallback | 會碰相同 media image 模組，但已讀相關 patch 未修改編碼轉色／EXIF 順序 |
| [#57752](https://github.com/vllm-project/vllm/pull/57752)，open，標題註明 Don't merge／Experiment | 把媒體 decode 延後到 processor；保留解碼時 normalize，再轉色 | 大範圍重構同區路徑，不能視為已落地修正；已讀相關 patch 未修正這個編碼假設 |

前五件新取回的 PR head：

| PR | head SHA |
| --- | --- |
| #44974 | `432234bf4efc1888c9349db43c07d770b2db0ef5` |
| #47566 | `1295988f9f3a4234b1d1f32aa1491f02b7057b0c` |
| #62418 | `77a80e2f7d7aecea988d04f64b861305bbee72cf` |
| #63369 | `bed2e4f6f9eb71cd97061997d91fa827b2b46397` |
| #57752 | `436e470cd75b923c98e395aa41d4c9180e07bad1` |

## 相關 issue 不能直接算同一缺陷

- [#62420](https://github.com/vllm-project/vllm/issues/62420)，open：描述 Mistral 模型的 JPEG EXIF 方向造成 token placeholder 不一致與 500，對應 #62418；沒有描述透明圖在編碼前合成而丟 EXIF。
- [#29645](https://github.com/vllm-project/vllm/issues/29645)，closed：正文只有 Qwen3-VL 旋轉影像擷取準確率下降的簡短敘述，缺少足以判斷 P01 根因的重現資料；不能排除或認定相同。
- [#19585](https://github.com/vllm-project/vllm/issues/19585)，closed：正文比較 InternVL3 在不同服務上的結果，未給出這個編碼／metadata 路徑的可核對重現。

## 限制與下一步

本輪閱讀上述五件 PR 的描述及 `multimodal/media`、`multimodal/image`、`multimodal/parse` 等相關檔案 patch；不是整份 PR 的 code review，也未逐則閱讀討論。#61986 使用同日上一輪已完整查核的資料。其餘搜尋命中多為 hashing、模型或效能題，只檢視標題，不據此宣稱全部無關。

搜尋索引可能尚未收錄新內容，未公開分支、Slack 討論或未提到這些關鍵詞的修正也可能漏掉。現有 open PR 隨時可改 head，這份紀錄不應當作日後的永久查重證明。

若探測可重現，下一步應先界定編碼 API 的預期契約，並用相同來源圖片比較直接 bytes 載入、PIL 輸入及 encode→decode 的方向與像素，再判斷是否確實是不同缺陷。特別要分開一般路徑和 #62418 所涉及的 Mistral 行為，避免把「一律旋轉」當成未經確認的通則。
