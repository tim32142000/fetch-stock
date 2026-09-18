# 開發過程中的紀錄

### GitHub Actions 排程延遲事件

在開發這個專案的過程中，剛好遇到一次 GitHub Actions 排程異常。

原本 workflow 設定為平日每天 06:10 UTC 執行，但在 2026 年 9 月期間，曾連續多次出現 scheduled workflow 延遲約 5～6 小時才被建立的情況。

進一步查看 workflow run 的時間後，發現 `created_at` 與 `run_started_at` 幾乎相同，因此比較不像是 runner 排隊造成，而是 scheduled workflow 本身較晚才被 GitHub 建立。

這次事件也讓我實際體會到，定時排程並不一定能保證準時執行；在設計依賴排程的系統時，也需要考慮外部平台延遲或異常的情況。

相關 GitHub Community 討論：
https://github.com/orgs/community/discussions/207346