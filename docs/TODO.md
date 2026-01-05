# タスク管理 (TODO)

## キャプティブポータル実装

- [ ] `main.py`: `DNSServer` の有効化 (インポート、初期化、start)。
- [ ] `web.py`: `handle_client` メソッド内にキャプティブポータル用のリダイレクトロジックを追加。
    - Host ヘッダーチェックの実装。
    - 特定パス (`/generate_204` 等) のリダイレクト実装。
- [ ] 動作確認: 実機 (iPhone, Android, PC) で Wi-Fi 接続時に自動的にページが開くか確認。