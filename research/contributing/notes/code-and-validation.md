# 從媒體輸入開始：程式入口與驗證成本

**第一輪建議（第二輪已完成）：先建立可執行的 Apple CPU 環境，再跑一個合成圖片測試。** `media/` 的確有不載入模型的測試，但不能因此把它當成免安裝 vLLM 的獨立 Python 小套件。

第二輪更新（2026-11-01）：[T01 實跑紀錄](../../tutorial-audit/records/T01.md)已完成 Mac CPU 安裝與圖片／base 共 23 件測試；以下保留第一輪靜態判讀，尚未實跑的範圍請對照 T01 的限制。

查核日期：2026-11-01。程式快照：`5d55ef1590c92213e3893dc8e8712f7f2e0bc508`。本輪只讀文件、程式與 CI 設定；沒有建置、下載模型或執行測試。下文的「事實」指在此快照看得到的行為或規則，「建議」是研究判斷，「待測」尚無本機結果。

## 先看懂請求經過哪裡

這張表是閱讀入口，不代表每個請求都會走過所有目錄。

| 問題表現 | 先讀的位置 | 這一層負責什麼 |
| --- | --- | --- |
| Python 呼叫推論 | `vllm/entrypoints/llm.py` | 離線 `LLM` 介面 |
| `vllm serve` 或 HTTP 請求 | `vllm/entrypoints/cli/`、`vllm/entrypoints/openai/` | CLI 與服務介面 |
| 聊天內容中的圖片網址 | `vllm/renderers/chat_utils/content_parser.py` | 將內容交給媒體連接器，記錄多模態項目 |
| 圖片、音訊、影片載入失敗 | `vllm/multimodal/media/` | 來源讀取、解碼、驗證、大小預算 |
| 圖片與提示詞對不上 | `vllm/multimodal/processing/` | 處理器輸出、佔位 token 與媒體資料的對應 |
| 排程、KV cache、執行協調 | `vllm/v1/core/`、`vllm/v1/engine/` | 推論核心 |
| 裝置執行、模型或 kernel | `vllm/v1/worker/`、`vllm/model_executor/`、`csrc/` | 工作程序、模型與底層運算 |

來源：[架構導覽][arch]、[聊天內容解析器][parser]、[多模態處理設計][processing]。表中的目錄用途依文件與程式對照整理。

聊天圖片的短路徑可以先記成：

```text
聊天內容解析器
  → MediaConnector.fetch_image / fetch_image_async
  → ImageMediaIO
  → Pillow 圖片與原始 bytes
  → 後續多模態處理
```

這是閱讀用的簡圖。`parse_image()` 會呼叫連接器並把圖片加入 tracker；同步與非同步解析器各有對應路徑。它不是模型完整執行流程。[來源：解析器][parser]

## `media/` 裡誰負責什麼

| 檔案 | 主要責任 | 修正時要追到哪裡 |
| --- | --- | --- |
| `base.py` | `MediaIO` 介面、`MediaWithBytes`、共用解碼預算 | 所有使用同一預算的媒體類型 |
| `connector.py` | HTTP、data URL、本機檔案來源；來源限制與下載錯誤 | `connections.py`、聊天解析器、同步與非同步呼叫 |
| `image.py` | 圖片解碼、模式轉換、base64 與 embedding | `multimodal/image.py` 的共用圖片處理 |
| `audio.py` | 音訊解碼、取樣率與解碼限制 | PyAV、soundfile、TorchCodec 路徑 |
| `video.py` | 影片載入參數、影格與 metadata、embedding | `multimodal/video.py` 與 `video_decoders/` |
| `__init__.py` | 對外匯出媒體類別 | import 會一併載入多個媒體模組 |

來源：[media 目錄][media]、[圖片實作][image]、[音訊實作][audio]、[影片實作][video]、[匯出入口][exports]。

**事實：不是每種媒體錯誤都應一律轉成 HTTP 400。** `connector.py` 把部分永久性下載錯誤轉成 422；408、429、5xx、DNS 與連線等暫時性錯誤保留原例外，讓後續流程處理。選題前必須確認錯誤來自下載、解碼還是請求驗證。[來源：錯誤轉換函式][connector]

**建議：第一題先讀圖片解碼與既有測試。** 它有合成小圖片、明確像素比較及壞資料案例，較容易建立可解釋的預期結果。這不表示已發現 bug，也不保證只改這一層就足夠。

## Mac 能做什麼：官方支援與本機證據分開

| 項目 | 已查證事實 | 尚不能宣稱的事 |
| --- | --- | --- |
| Apple Silicon CPU | 官方列為實驗性支援；須從原始碼建置，沒有 Apple CPU 預建 wheel | 此工作區已成功安裝 |
| 工具鏈 | 文件列 macOS Sonoma 以上、Xcode 15.4 以上、Apple Clang 15 以上 | 所有版本組合都通過 |
| 資料型別 | Apple CPU 文件列 FP32、FP16 | 所有模型與算子都支援 |
| Metal | 文件指向社群維護的 `vllm-metal` 外掛 | 主倉 CPU 測試結果等於 Metal 測試結果 |
| Python-only 開發 | CPU 文件說這種方式需要對應平台的預建 wheel | 設 `VLLM_USE_PRECOMPILED=1` 就能免編譯安裝 Apple CPU |

來源：[固定快照 Apple 安裝頁][apple]、[CPU 安裝頁原始碼][cpu]；另於本日開啟[官方線上 CPU 文件][live-cpu]，確認 Apple 實驗性支援與無預建 wheel 的說明仍在。

**事實：macOS smoke test 並沒有跑媒體測試集。** 工作流每天排程或手動啟動，使用 Python 3.12，建置 CPU 版後啟動縮小的 Qwen3-0.6B 服務；權重採 dummy，檢查健康端點與文字 completion。設定中 macos-15 為必要項，macos-26 為非阻塞項。這能證明工作流的驗證範圍，不能代替實際執行結果。[來源：macOS 工作流][mac-ci]

**待測：** 本機冷建置時間、套件解析是否成功、媒體 codec 是否可用，以及單一測試收集時是否會遇到平台 import 問題。

## 為什麼只跑一個圖片測試仍需要完整環境

`tests/conftest.py` 在收集測試時就匯入 `torch`、Transformers、`vllm.LLM`、模型測試工具及多種 vLLM 模組。它也設置自動執行的測試前後處理，包括 HTTP client 行為、全域清理與 Dynamo reset。測試本體沒建立模型，不代表收集階段只需要 Pillow。[來源：共用 conftest][conftest]

`vllm.multimodal.media.__init__` 也同時匯入音訊、圖片、影片及連接器。圖片實作本身匯入 Torch 與 vLLM 工具。直接改成單檔動態載入以繞過正常 import，不能證明使用者實際呼叫路徑正常。[來源：匯出入口][exports]、[圖片實作][image]

依賴檔另有一個容易誤讀的地方：

- `requirements/cpu.txt` 是 CPU 執行環境，含 Torch、torchvision、torchaudio、TorchCodec 等條件依賴。[來源][cpu-req]
- `requirements/test/cpu.txt` 的檔頭記錄，它是從 `cuda.in` 針對 Linux x86_64、Python 3.12 解析的結果。不能因為檔名有 CPU 就當成 macOS 鎖檔。[來源][test-cpu]
- `AGENTS.md` 指示非 x86_64 測試環境使用 `requirements/test/cuda.in`；該檔除了 pytest，也包含模型評估與音訊等許多依賴。它的名稱不表示所有依賴都只給 CUDA，但也不能保證 Mac 可完整安裝。[來源][agents]、[測試依賴來源][test-input]

下一輪應先驗證安裝與收集，再決定需要哪些測試。這一輪沒有自行發明或驗證「最小安裝套件清單」。

## 六個媒體測試檔的實際成本

| 測試檔 | 快照中的選取狀態 | 可見的額外成本 | 初次用途 |
| --- | --- | --- | --- |
| `test_image.py` | 全檔 `cpu_test`、`skip_global_cleanup` | Pillow、NumPy；有合成圖片與本機資產 | 優先選單一合成圖片測試 |
| `test_base.py` | 全檔 `cpu_test` | repo 內 `assets/image1.png`；pickle roundtrip | 第二個較小基線 |
| `test_audio.py` | 全檔 `cpu_test` | 音訊資產、soundfile、TorchCodec/PyAV 路徑；部分案例用影片 | 環境穩定後再展開 |
| `test_video.py` | 全檔 `cpu_test` | OpenCV、影片資產與 decoder；部分案例檢查 GPU backend 參數 | 先看個別測試，別把整檔視為免依賴 |
| `test_unprocessable_entity_error.py` | 全檔 `cpu_test`、`skip_global_cleanup` | 匯入服務錯誤回應函式；多個外部 HTTP 行為用 mock | 用於理解錯誤分類，不能取代端到端證據 |
| `test_connector.py` | 未設全檔或個別 `cpu_test` | 本機 HTTP server、公開圖片/影片下載、同步與非同步 | 不會被 `-m cpu_test` 選到 |

來源：[媒體測試目錄][media-tests]；各列是靜態閱讀，未量測耗時，也未保證整個檔案在 Mac 通過。

**事實：本機 HTTP server 不代表完全離線。** connector 測試的圖片 fixture 會用 `ImageAsset` 取得素材；資產不存在快取時，`get_vllm_public_assets()` 會從公開 S3 下載。音訊與影片測試也會讀取資產。[來源：connector 測試][connector-test]、[圖片資產][assets-image]、[下載與快取][assets-base]

**建議：** 第一個基線選 `test_image_media_io_rgb_png_transparency`。它自行建立 2×1 圖片，用 Pillow 合成作參考並精確比較陣列，不呼叫模型，也不在測試本體下載資產。這只描述測試本體；正常 pytest 收集與共用 fixture 仍需要前述環境。[來源：圖片測試][image-test]

## CPU 標記與 CI 是兩件事

- `cpu_test` 的登記說明是 CPU-only 測試，但它只是測試選取標記，不是自動修復環境或跨平台保證。[來源：pytest 設定][pytest-config]
- Buildkite 的 `(CPU) Multimodal + Config` 選取 `-m cpu_test multimodal`，來源相依含 `vllm/multimodal/` 與 `tests/multimodal`。[來源：misc CI][misc-ci]
- 同檔另有 `-m 'not cpu_test' multimodal` 的 GPU 工作，會涵蓋沒有 CPU 標記的 connector 測試。這不證明 connector 的每個案例都必須使用 GPU，只表示現有分流如此。[來源：misc CI][misc-ci]
- `tests/models/multimodal/processing` 有另一組 CPU 分片；其中 `test_tensor_schema.py` 被排除，另由 GPU 工作選取。不能把它與 `tests/multimodal/media` 混為同一驗證範圍。[來源：模型多模態 CI][model-ci]
- `tests/AGENTS.md` 明文要求檢查 CI 指令、marker 與來源相依是否涵蓋新增測試；檔案存在不等於 CI 會跑。[來源：測試規則][test-rules]

## 第一輪提出的最小基線

先以目前快照建立獨立的實跑工作目錄與 `.venv`，保存以下四個關卡；不要一開始跑整個 `tests/`。

| 關卡 | 要取得的證據 | 通過後做什麼 |
| --- | --- | --- |
| 1. 工具鏈與環境 | Python、Apple Clang、套件版本與安裝指令；不記錄私人機台識別 | 確認能正常 `import vllm` |
| 2. 正常 pytest 收集 | 指定單一測試能收集，沒有跳過正常 conftest | 才執行該測試 |
| 3. 合成圖片基線 | 原始快照的 pass/fail、耗時、完整錯誤 | 再跑 pickle 基線與圖片檔案 |
| 4. 擴大到來源路徑 | connector 的同步/非同步、本機或公開資產需求 | 依實際問題挑選相關測試 |

環境已依官方文件建立並安裝所需測試依賴後，可從 repo 根目錄試以下指令。**這是第一輪規劃的指令；實際執行版本、結果與重現步驟見 [T01](../../tutorial-audit/records/T01.md)。**

```bash
.venv/bin/python -c 'import vllm; print(vllm.__version__)'
.venv/bin/python -m pytest --collect-only -q \
  tests/multimodal/media/test_image.py::test_image_media_io_rgb_png_transparency
.venv/bin/python -m pytest -v \
  tests/multimodal/media/test_image.py::test_image_media_io_rgb_png_transparency
.venv/bin/python -m pytest -v \
  tests/multimodal/media/test_base.py::test_media_with_bytes_pickle_roundtrip
```

環境管理使用 `uv`，執行使用 `.venv/bin/python`，遵守[專案指示][agents]。下一輪實跑記錄應存到 `research/tutorial-audit/records/`，並更新對應清單；此處不預填通過結果。

### 停止擴大範圍的條件

以下是研究建議，不是官方門檻：

1. 若安裝或收集失敗，先記錄阻塞，再確認是環境、依賴還是程式問題；不要藉由移除 conftest、偽造模組或改 skip 來宣稱測試通過。
2. 若下一步需要尚未具備的 codec、平台或模型資源，保留可重現錯誤與需求，停止擴大測試範圍。
3. 若候選修正會改變 HTTP 回應、使用者輸入結果或模型輸出，先確認能否提供真正入口的回歸證據，再決定投入。單元測試可能足以定位，未必足以提交。
4. 若疑似問題涉及資料外洩或資源耗盡，先讀專案安全回報流程，不把敏感重現材料直接公開。

第 1、3 項也呼應官方要求：測試真物件、重現修正前失敗；使用者可見行為至少需經 `LLM` 或 `RemoteOpenAIServer` 的回歸測試，載入行為涉及權重時使用真權重。[來源：測試規則][test-rules]

## 這輪結論的邊界

可以確認：媒體區有小型、CPU 標記、非模型的測試入口；目前 CI 有 CPU 分流；Apple 平台仍有建置與依賴成本。不能確認：使用者 Mac 能跑哪些完整測試、需要多久、哪一題是未被修掉的 bug。

沒有新 bug 結論，沒有對外認領，也沒有做模型品質、效能或 GPU 驗證。本筆記的下一步是取得最小本機測試基線，而非直接提交修正。

## 固定快照來源

[arch]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/design/arch_overview.md
[parser]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/renderers/chat_utils/content_parser.py
[processing]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/design/mm_processing.md
[media]: https://github.com/vllm-project/vllm/tree/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/multimodal/media
[image]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/multimodal/media/image.py
[audio]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/multimodal/media/audio.py
[video]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/multimodal/media/video.py
[exports]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/multimodal/media/__init__.py
[connector]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/multimodal/media/connector.py
[apple]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/getting_started/installation/cpu.apple.inc.md
[cpu]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/docs/getting_started/installation/cpu.md
[live-cpu]: https://docs.vllm.ai/en/latest/getting_started/installation/cpu/
[mac-ci]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.github/workflows/macos-smoke-test.yml
[conftest]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/tests/conftest.py
[cpu-req]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/requirements/cpu.txt
[test-cpu]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/requirements/test/cpu.txt
[test-input]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/requirements/test/cuda.in
[agents]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/AGENTS.md
[media-tests]: https://github.com/vllm-project/vllm/tree/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/tests/multimodal/media
[connector-test]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/tests/multimodal/media/test_connector.py
[assets-image]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/assets/image.py
[assets-base]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/vllm/assets/base.py
[image-test]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/tests/multimodal/media/test_image.py
[pytest-config]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/pyproject.toml
[misc-ci]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.buildkite/test_areas/misc.yaml
[model-ci]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/.buildkite/test_areas/models_multimodal.yaml
[test-rules]: https://github.com/vllm-project/vllm/blob/5d55ef1590c92213e3893dc8e8712f7f2e0bc508/tests/AGENTS.md
