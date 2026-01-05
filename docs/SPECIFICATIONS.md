# 仕様書

## ログ記録

- ログファイル: `/log.txt`
- 最大サイズ: 5120 bytes
- 書き込み方式: 追記
- サイズ超過時の動作: `log.txt` を空にしてから追記

## エラー応答

- `MemoryError`
  - `gc.collect()` を実行
  - 応答: `503 Service Unavailable`
- `OSError`
  - 応答: `500 Internal Server Error`
- `ValueError`
  - 応答: `400 Bad Request`
- その他の例外
  - 応答: `500 Internal Server Error`

## ログ閲覧

- ルート: `/admin/log`
- 応答: `/log.txt` の内容を `text/plain` で返す
- ファイル未存在時は空文字を返す

## DisplayController

- 生成時に OLED を初期化する。
- `show_qr_code(ip, ssid, passwd)`
  - QR を生成してキャッシュ
  - 生成後に `unload_modules()` を呼ぶ
- `start_display_cycle()`
  - 120 秒 ON / 1 秒 OFF のループ
- `display_off()` / `display_on()`
  - OLED の ON/OFF を制御する

## 職務経歴保存

- /admin/jobhist の保存はメモリ消費を抑えた逐次書き込みを行う。
- データが 0 件の場合は既存の jobhist.csv を保持する。
