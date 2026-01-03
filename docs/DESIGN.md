# Design

## Web Server Configuration

### Frontend

- HTML, CSS, JavaScript で構築。
- モダンなデザインを採用。
- `crud-base.js` を共通化し、CRUD 操作を簡素化。
- 編集ページのフォームは複数行に対応し、動的に増減可能。
- **ページ構成**:
  - トップページ (`/`): 履歴書表示
  - ユーザプロフィール編集ページ (`/admin/user`): ユーザ情報編集・画像アップロード
  - 学歴・職歴編集ページ (`/admin/simplehist`): 学歴・職歴編集
  - 詳細職歴編集ページ (`/admin/jobhist`): 詳細職歴編集
  - ポートレイト編集ページ (`/admin/portrait`): ポートレイト編集
  - キャプティブポータル検出 (`/hotspot-detect.html`): 一部デバイス用

### Backend

- MicroPython で構築。
- Web サーバは、`uasyncio` を使用した非同期処理。
- クリーンアーキテクチャを意識しつつ、リソース制約に合わせて最適化。
- ディスプレイ制御は `display.py` に分離。

## Directory Structure

```text
.
├── display.py             # OLED ディスプレイ制御
├── dns.py                 # DNS サーバ (キャプティブポータル用)
├── data/                  # データ保存ディレクトリ
│   ├── jobhist.csv        # 詳細職歴データ
│   ├── simplehist.csv     # 学歴・職歴データ
│   ├── portrait.csv       # ポートレイトデータ
│   └── user.csv           # ユーザ基本情報
├── docs/                  # ドキュメント
│   ├── DesignDocs.md      # 本ドキュメント (Deprecated)
│   ├── REQUIREMENTS.md    # 要件定義
│   ├── SPECIFICATIONS.md  # 仕様書
│   ├── DESIGN.md          # 設計書
│   └── pico1w-resumaker.jpg
├── lib/                   # ライブラリ
│   ├── ssd1351.py         # OLED ディスプレイドライバ
│   ├── uQR.py             # QR コード生成
│   └── litefont/          # フォント関連
├── main.py                # メインスクリプト
├── README.md              # プロジェクト概要
├── secrets.py             # 設定情報
├── storage.py             # CSV データ管理
├── web.py                 # Web サーバ実装
└── www/                   # Web コンテンツ
    ├── index.html         # トップページ雛形
    ├── index.js           # トップページスクリプト
    ├── user.html          # ユーザ情報ページ雛形
    ├── user.js            # ユーザ情報スクリプト
    ├── simplehist.html    # 簡易職歴ページ雛形
    ├── simplehist.js      # 学歴・職歴スクリプト
    ├── jobhist.html       # 詳細職歴ページ雛形
    ├── jobhist.js         # 詳細職歴スクリプト
    ├── portrait.html      # ポートレイトページ雛形
    ├── portrait.js        # ポートレイトスクリプト
    ├── crud-base.js       # CRUD 共通スクリプト
    ├── hotspot-detect.html# キャプティブポータル検出用
    ├── style.css          # スタイルシート
    └── image.jpg          # アップロードされた顔写真 (存在する場合)
```
