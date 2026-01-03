# Specifications

## Technical Stack

### Hardware

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

### Software

以下を遵守

- **フロントエンド**: HTML, CSS, JavaScript
- **バックエンド**: MicroPython

## Constraints

- ストレージ容量: 最大 2MB
- 外部ライブラリ: 使用不可 (vendoring は可)
- ディスプレイ: 128x128 ドットの解像度
- Wi-Fi: アクセスポイントモードのみ (インターネット接続なし)

## Interface

### Web Routing

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

## Data Models

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

### `portrait.csv` (ポートレイト情報)

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

## Functional Requirements

### Top Page (`/`)

- `user.csv`, `simplehist.csv`, `jobhist.csv` のデータが全て揃っている場合、履歴書を表示。
- いずれかのファイルが空または存在しない場合、「データなし」メッセージを表示 (または一部表示)。
- 各 API は CSV ファイルを読み取り JSON で返す。
- フロントエンドは JSON を受け取り、履歴書デザインに整形する。

### User Info Edit Page (`/admin/user`)

#### GET

- ユーザ情報の編集フォームを表示。
- `user.csv` の全カラムに対応した入力フォームを提供。
- 画像アップロード機能を提供 (プレビュー付き)。
- `user.csv` を読み込み、フォームに規定値として代入。
- 保存ボタンで `/admin/user` へ POST (画面遷移なし)。
- POST 時に JSON で送信。
- JavaScript で実装。

#### POST

- parse して CSV ファイルに保存

#### Image Upload

- `/api/upload` に対してチャンク分割してバイナリ送信。
- サーバ側で結合し `image.jpg` として保存。

### Education/Career Edit Page (`/admin/simplehist`)

#### GET

- 学歴・職歴の編集フォームを表示。
- `simplehist.csv` を読み込み、規定値として代入。
- 保存ボタンで `/admin/simplehist` へ JSON で POST (画面遷移なし)。
- JavaScript で実装。
- 複数行のフォームを動的に増減可能 (+/- ボタン)。

#### POST

- parse して CSV ファイルに保存

### Detailed Job History Edit Page (`/admin/jobhist`)

#### GET

- 詳細職歴の編集フォームを表示。
- `jobhist.csv` を読み込み、フォームの規定値として代入。
- 保存ボタンで `/admin/jobhist` へ JSON で POST (画面遷移なし)。
- JavaScript で実装。
- 複数行のフォームを動的に増減可能 (+/- ボタン)。

#### POST

- parse して CSV ファイルに保存

### Portrait Edit Page (`/admin/portrait`)

#### GET

- `portrait.csv` を読み込み、フォームの規定値として代入。
- 保存ボタンで `/admin/portrait` へ JSON で POST (画面遷移なし)。
- JavaScript で実装。
- 複数行のフォームを動的に増減可能 (+/- ボタン)。

#### POST

- parse して CSV ファイルに保存
