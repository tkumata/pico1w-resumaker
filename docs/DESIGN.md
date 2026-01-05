# 設計書

## 概要

- 例外処理とログ記録を `lib/logger.py` に集約する。
- OLED の状態管理を `DisplayController` に集約する。
- 職務経歴保存はメモリ使用量を抑えて書き込む。

## ロガー設計

- 実装場所: `lib/logger.py`
- 保存先: `/log.txt`
- 最大サイズ: 5120 bytes
- サイズ超過時: クリア後に追記する。
- 例外時: ログ書き込み自体のエラーは握りつぶす。

### 公開 API

- `error(message)`
  - 文字列化して `[ERR]` プレフィックス付きで 1 行追記する。

## Web サーバ設計

- `web.py` の `handle_client` で例外種別ごとに応答とログ記録を行う。
- `/admin/log` を追加し、`/log.txt` を `text/plain` で返す。
- `/admin` 静的配信の分岐で `/admin/log` を除外する。

## DisplayController 設計

- 実装場所: `display.py`
- インスタンス変数に状態を保持する。
  - `qr_cache`, `is_on`, `is_running`
- 初期化で SPI/Pin/OLED を構築する。
- 既存の関数はメソッド化する。
- QR 生成後に `unload_modules()` を呼ぶ。

## 職務経歴保存の設計

- `storage.py` の `write_jobhist` でメモリ使用量を抑えた書き込みを行う。
- 0 件保存要求のときはファイルを書き換えない。

## 影響範囲

- `lib/logger.py` 新規追加。
- `web.py` の例外処理とルーティング追加。
- `display.py` をクラス化。
- `main.py` の呼び出し変更。
