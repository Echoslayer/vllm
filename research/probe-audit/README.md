# 探測式查核：從輸入邊界找可重現問題

已完成圖片邊界探測與真實 parser／data URL connector 比較，並獨立重現 benchmark PIL／bytes 分支的方向差異。已建立研究候選卡，尚未修正或投稿。

| 編號 | 假設 | 輸入與指令 | 觀察結果 | 紀錄 |
| --- | --- | --- | --- | --- |
| P02 | 換輸入表示是否改變方向？ | 6 組 helper 路徑、3 種 benchmark 表示 | parser／data URL connector 與 benchmark 獨立分支重現寬高差異 | [呼叫端與證據](records/P02.md) |
| P01 | PNG 編碼往返應保留顯示方向？ | 小型 RGB／RGBA／LA PNG，腳本見紀錄 | 24 組中 21 組方向不符；另 10 組透明背景符合參照 | [證據與限制](records/P01.md) |

每次探測在 `records/` 留下日期、程式版本、必要環境、假設、預期、實際結果與判斷依據。把已確認缺陷、正常行為和未確認觀察分開；不把猜測當成產品 bug。只保存可公開資料。

依 ISO 24495-1 淺白語言原則編寫。確認問題後先查重複 issue 與 PR，再放入[提案總表](../../proposals/README.md)。這是個人研究；研究分支永遠不開上游 PR。
