# 履歴書アプリ - DesignDocs

|            |                  |
| ---------- | ---------------- |
| **Author** | Tomokatsu Kumata |
| **Date**   | 2025-06-23       |
| **Update** | 2026-01-02       |
| **Status** | Implemented      |

## プロンプト

Raspberry Pi Pico W で開発します。次の DesignDocs に従って指定されたファイルを全て必ず生成してください。正しいコードを生成してください。使用言語は MicroPython と JavaScript と HTML と CSS です。DesignDocs は絶対に守ってください。コードの生成が無理なら、この DesignDocs の足りない部分の日本語で指摘してください。

## 概要

Raspberry Pi Pico W を用いて、履歴書の作成・編集・削除・共有ができるスタンドアロンガジェットを開発します。
本デバイスは Wi-Fi アクセスポイントとして動作し、Web ブラウザ経由で履歴書の閲覧・管理を可能にします。

## 背景

### 課題

- 履歴書作成には手書きやテンプレート探しに手間がかかる。
- アプリ依存のソリューションは環境変化で使用不可になるリスクがある。
- 作成した履歴書は印刷しないと共有が難しい。

### 解決策

ポータブルでデジタル化された履歴書を即座に共有可能なガジェットを開発する。

## 目的

- Raspberry Pi Pico W を Wi-Fi アクセスポイントモードで起動
- Web サーバとして以下の機能を提供：
  - 履歴書の作成、編集、削除
  - HTML/CSS で生成された履歴書の閲覧および共有
  - 証明写真のアップロードと表示

## 目標

- 目の前にいる相手にのみ履歴書を共有可能。
- 履歴書データの作成、編集、削除が管理画面から可能。
- HTML/CSS を使用して履歴書を生成。
- トップページにアクセスすると履歴書を生成する。

## 非目標

- サインインやログイン機能の実装は不要。
- 応答速度 (レイテンシ) の最適化は優先しない (利用者は 1〜2 人を想定)。
- セキュリティ対策は行わない (常時インターネット接続しないため)。
- クリーンアーキテクチャなどに準拠してファイルを細かく分けると Pico W にファイル読み込みのオーバーヘッドがかかり無駄にメモリ消費するので、最低限の分け方で留めておく。

## ユースケース

- ユーザが Pico W の Wi-Fi アクセスポイントに接続し、ブラウザで以下の URL にアクセスすることで履歴書を閲覧・管理可能:
  - `http://192.168.4.1`: トップページ (履歴書)
  - `http://192.168.4.1/admin/user`: ユーザプロフィール編集画面 (画像アップロード含む)
  - `http://192.168.4.1/admin/simplehist`: 学歴・職歴編集画面
  - `http://192.168.4.1/admin/jobhist`: 詳細職歴編集画面
  - `http://192.168.4.1/admin/portrait`: ポートレイト編集画面

## 技術スタック

### ハードウェア

- **Raspberry Pi Pico W**: メイン処理装置。
- **SSD1351 OLED ディスプレイ**: Wi-Fi アクセスポイントの情報を表示 (解像度: 128x128 ドット)。
- PIN は以下のとおり。

```python
spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
dc = Pin(16, Pin.OUT)
cs = Pin(20, Pin.OUT)
rst = Pin(17, Pin.OUT)

display = SSD1351(128, 128, spi, dc, cs, rst)
```

### ソフトウェア

以下を遵守

- **フロントエンド**: HTML, CSS, JavaScript
- **バックエンド**: MicroPython

## 制約

- ストレージ容量: 最大 2MB
- 外部ライブラリ: 使用不可 (vendoring は可)
- ディスプレイ: 128x128 ドットの解像度
- Wi-Fi: アクセスポイントモードのみ (インターネット接続なし)

## Web サーバ構成

### フロントエンド

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

### バックエンド

- MicroPython で構築。
- Web サーバは、`uasyncio` を使用した非同期処理。
- クリーンアーキテクチャを意識しつつ、リソース制約に合わせて最適化。
- ディスプレイ制御は `display.py` に分離。

### ディレクトリ構成

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
│   ├── DesignDocs.md      # 本ドキュメント
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

## データモデル

データは `/data/` ディレクトリに CSV 形式で保存。各 CSV ファイルは以下のカラムを持つ。

### `user.csv` (ユーザ基本情報)

| Column            | Format     | Content          |
| ----------------- | ---------- | ---------------- |
| `usr_name`        | string     | ユーザの名前     |
| `usr_name_kana`   | string     | ユーザの名前(かな)|
| `usr_gender`      | 0 or 1     | 性別 (0:男, 1:女)|
| `usr_birthday`    | YYYY-MM-DD | 誕生日           |
| `usr_age`         | num        | 年齢             |
| `usr_addr`        | string     | 住所             |
| `usr_phone`       | num        | 電話番号         |
| `usr_mobile`      | num        | 携帯番号         |
| `usr_email`       | string     | メールアドレス   |
| `usr_family`      | 0 or 1     | 扶養家族の有無   |
| `usr_licenses`    | string     | 免許・資格       |
| `usr_siboudouki`  | string     | 志望動機         |
| `usr_hobby`       | string     | 趣味             |
| `usr_skill`       | string     | 特技             |
| `usr_access`      | string     | 出社にかかる時間 |

**例**:

```csv
kumata,くまた,0,1999-01-02,26,神奈川県川崎市...,090...,example@example.com,0,運転免許,志望動機...,趣味...,特技...,1時間
```

### `simplehist.csv` (学歴・職歴)

複数行保存可能。編集ページでフォームを動的に増減。

| Column          | Format     | Content                      |
| --------------- | ---------- | ---------------------------- |
| `hist_no`       | int        | シーケンス番号               |
| `hist_datetime` | YYYY-MM-DD | 入社日・退社日               |
| `hist_status`   | string     | status (入学/卒業/入社/退社) |
| `hist_name`     | string     | 企業名                       |

**例**:

```csv
1,1993-04-01,入学,xxx大学xxx学部xxx学科
2,1997-03-31,卒業,xxx大学xxx学部xxx学科
3,1997-04-01,入社,株式会社xxx
4,2001-06-21,退社,株式会社xxx
```

### `jobhist.csv` (詳細職歴)

複数行保存可能。編集ページでフォームを動的に増減。

| Column               | Format               | Content           |
| -------------------- | -------------------- | ----------------- |
| `job_no`             | int                  | sequential number |
| `job_name`           | string               | company name      |
| `job_description`    | string (改行 `<br>`) | description       |

**例**:

```csv
1,株式会社xxx,これまでにやったこと。<br>- aaa<br>- bbb
2,株式会社yyy,これまでにやったこと。<br>- aaa<br>- bbb
3,株式会社zzz,これまでにやったこと。<br>- aaa<br>- bbb
```

## `portrait.csv` (ポートレイト情報)

| Column             | Format | Content           |
| ------------------ | ------ | ----------------- |
| `portrait_no`      | int    | sequential number |
| `portrait_url`     | string | Portrait URL      |
| `portrait_summary` | string | Portrait summary  |

**例**:

```csv
1,https://github.com/youraccount/projectname1,blah blah blah
2,https://github.com/youraccount/projectname2,blah blah blah
```

## インターフェイス

### Web ルーティング

| Method    | URI                     | Summary                  |
| --------- | ----------------------- | ------------------------ |
| GET       | `/`                     | 履歴書トップページ       |
| GET       | `/hotspot-detect.html`  | キャプティブポータル検出 |
| GET, POST | `/admin/user`           | ユーザ情報編集ページ     |
| GET, POST | `/admin/simplehist`     | 学歴・職歴編集ページ     |
| GET, POST | `/admin/jobhist`        | 詳細職歴編集ページ       |
| GET, POST | `/admin/portrait`       | ポートレイト編集ページ   |
| GET       | `/api/user`             | ユーザ情報取得           |
| GET       | `/api/simplehist`       | 学歴・職歴取得           |
| GET       | `/api/jobhist`          | 詳細職歴取得             |
| GET       | `/api/portrait`         | ポートレイト取得         |
| POST      | `/api/upload`           | 画像アップロード         |

- フロントエンドは JavaScript で構築し、モダンなデザインを採用。
- 各編集ページ (`/admin/*`) は対応する CSV ファイルを編集可能。
- `/api/upload` はチャンク分割アップロードに対応。

## 機能要件

### トップページ (`/`)

- `user.csv`, `simplehist.csv`, `jobhist.csv` のデータが全て揃っている場合、履歴書を表示。
- いずれかのファイルが空または存在しない場合、「データなし」メッセージを表示 (または一部表示)。
- 各 API は CSV ファイルを読み取り JSON で返す。
- フロントエンドは JSON を受け取り、履歴書デザインに整形する。

### ユーザ情報編集ページ (`/admin/user`)

#### GET 時

- ユーザ情報の編集フォームを表示。
- `user.csv` の全カラムに対応した入力フォームを提供。
- 画像アップロード機能を提供 (プレビュー付き)。
- `user.csv` を読み込み、フォームに規定値として代入。
- 保存ボタンで `/admin/user` へ POST (画面遷移なし)。
- POST 時に JSON で送信。
- JavaScript で実装。

#### POST 時

- parse して CSV ファイルに保存

#### 画像アップロード

- `/api/upload` に対してチャンク分割してバイナリ送信。
- サーバ側で結合し `image.jpg` として保存。

### 学歴・職歴編集ページ (`/admin/simplehist`)

#### GET 時

- 学歴・職歴の編集フォームを表示。
- `simplehist.csv` を読み込み、規定値として代入。
- 保存ボタンで `/admin/simplehist` へ JSON で POST (画面遷移なし)。
- JavaScript で実装。
- 複数行のフォームを動的に増減可能 (+/- ボタン)。

#### POST 時

- parse して CSV ファイルに保存

### 詳細職歴編集ページ (`/admin/jobhist`)

#### GET 時

- 詳細職歴の編集フォームを表示。
- `jobhist.csv` を読み込み、フォームの規定値として代入。
- 保存ボタンで `/admin/jobhist` へ JSON で POST (画面遷移なし)。
- JavaScript で実装。
- 複数行のフォームを動的に増減可能 (+/- ボタン)。

#### POST 時

- parse して CSV ファイルに保存

### ポートレイト編集画面 (`/admin/portrait`)

#### GET 時

- `portrait.csv` を読み込み、フォームの規定値として代入。
- 保存ボタンで `/admin/portrait` へ JSON で POST (画面遷移なし)。
- JavaScript で実装。
- 複数行のフォームを動的に増減可能 (+/- ボタン)。

#### POST 時

- parse して CSV ファイルに保存

## AI が生成すべき

絶対に以下を生成すること。

- main.py
- secrets.py
- storage.py
- web.py
- index.html
- index.js
- jobhist.html
- jobhist.js
- simplehist.html
- simplehist.js
- style.css
- user.html
- user.js
- portrait.html
- portrait.js
- crud-base.js
