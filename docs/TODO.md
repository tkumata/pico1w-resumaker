# リファクタリング計画

本プロジェクトにおける主要なアンチパターン（例外の握りつぶし、グローバル変数の乱用）を解消するための実装タスクリスト。

## 1. 例外処理の適正化 (B: Broad Exception Handling)

現状、`web.py` などで `except Exception` により全てのエラーをキャッチし、`print` するだけの処理となっている。
これを改善し、特定のエラーをハンドリングすると同時に、PC 未接続時でもエラーを確認できるようにファイルベースのロギングを実装する。

### 設計方針

- **Logger クラスの作成**: エラーログを Flash メモリ（`log.txt`）に書き込む簡易クラスを作成。
- **特定例外のキャッチ**: `MemoryError`, `OSError` など想定されるエラーを個別に処理。
- **ログ閲覧機能**: Web 管理画面からログを確認できる機能を追加。

### タスク

- [ ] **`lib/logger.py` の実装**
    - シングルトンまたは単純なモジュールとして実装。
    - `log.txt` への追記モード書き込み。
    - ファイルサイズ制限（例: 5KB を超えたらローテートまたはクリア）を設けて Flash 溢れを防止。
    ```python
    # 実装イメージ
    import os
    LOG_FILE = "/log.txt"
    MAX_SIZE = 5120

    def error(message):
        try:
            # サイズチェックと書き込み処理
            with open(LOG_FILE, "a") as f:
                f.write(f"[ERR] {message}\n")
        except:
            pass
    ```

- [ ] **`web.py` のリファクタリング**
    - `logger` をインポート。
    - `handle_client` 内の `except Exception` ブロックを分解。
    - **MemoryError**: `gc.collect()` を実行し、503 または 500 エラーを返す。ログ記録。
    - **OSError**: ファイル I/O エラー。ログ記録。
    - **ValueError**: JSON パースエラーなど。400 Bad Request を返す。ログ記録。
    - **その他 Exception**: 予期せぬエラーとしてログ記録（スタックトレースはメモリを食うのでメッセージのみ推奨）。

- [ ] **管理用ログ閲覧ルートの追加**
    - `web.py` にルート `/admin/log` を追加。
    - `log.txt` の内容を読み込んでブラウザに表示するハンドラを実装。

## 2. 状態管理のカプセル化 (D: Global State Management)

`display.py` 内で `qr_cache`, `display_on`, `display_cycle_running` などのグローバル変数が散乱しており、状態遷移が追いづらい。
これをクラス化し、状態と操作をまとめる。

### 設計方針

- **`DisplayController` クラス**: 全ての状態変数（キャッシュ、ON/OFF 状態）をインスタンス変数 (`self.*`) に持つ。
- **責務の集約**: 初期化、QR 生成、ON/OFF サイクル管理をメソッド化する。

### タスク

- [ ] **`display.py` の書き換え**
    - 既存の関数群を `DisplayController` クラスのメソッドに変換。
    ```python
    # 実装イメージ
    class DisplayController:
        def __init__(self):
            self.qr_cache = None
            self.is_on = True
            self.is_running = False
            self.display = SSD1351(...) # 初期化処理

        def show_qr(self, ip, ssid, password):
            # QR生成とキャッシュ、描画
            pass

        async def start_cycle(self):
            self.is_running = True
            while self.is_running:
                # 120秒 ON, 1秒 OFF のループ処理
                # self.is_on フラグを管理
                pass
        
        def stop(self):
            self.is_running = False
    ```
    - `unload_modules` の処理がクラスインスタンスに悪影響を与えないよう、依存関係（`uQR`）のスコープを確認・調整する。

- [ ] **`main.py` の修正**
    - グローバル関数呼び出し (`display.show_qr_code` 等) を廃止。
    - インスタンス生成とメソッド呼び出しに変更。
    ```python
    # 変更イメージ
    from display import DisplayController
    
    # ...
    disp_ctrl = DisplayController()
    disp_ctrl.show_qr(ip, secrets.SSID, secrets.PASSWORD)
    
    asyncio.gather(
        web_server.start(),
        disp_ctrl.start_cycle(),
    )
    ```

