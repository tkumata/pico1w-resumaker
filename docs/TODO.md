# リファクタリング計画

本プロジェクトにおける主要なアンチパターン（例外の握りつぶし、グローバル変数の乱用）を解消するための実装タスクリスト。

## 1. 例外処理の適正化 (B: Broad Exception Handling)

### 設計方針

- Logger クラスの作成: エラーログを Flash メモリ（`/log.txt`）に書き込む簡易モジュールを作成。
- 特定例外のキャッチ: `MemoryError`, `OSError`, `ValueError` を個別に処理。
- ログ閲覧機能: Web 管理画面からログを確認できる機能を追加。

### タスク

- [x] `lib/logger.py` の実装
- [x] `web.py` のリファクタリング
- [x] 管理用ログ閲覧ルートの追加

## 2. 状態管理のカプセル化 (D: Global State Management)

### 設計方針

- `DisplayController` クラス: 全ての状態変数をインスタンス変数に持つ。
- 責務の集約: 初期化、QR 生成、ON/OFF サイクル管理をメソッド化する。

### タスク

- [x] `display.py` の書き換え
- [x] `main.py` の修正

## 3. /admin/jobhist 保存時の安定化

### 設計方針

- 職務経歴保存を逐次書き込みでメモリ使用量を抑える。
- 0 件保存要求は既存ファイルを保持する。

### タスク

- [x] `storage.py` の `write_jobhist` を修正
