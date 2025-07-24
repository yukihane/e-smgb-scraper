# 血糖値データスクレイピングツール

ASP.NET SPAサイト（https://cloud.e-smbg.net/）から血糖値データを自動取得するPythonスクレイピングツールです。

## 機能

- ASP.NET特有のViewState/EventValidationパラメータの自動処理
- 自動ログイン機能
- 血糖値データの自動抽出
- 年月指定での絞り込み機能
- JSON/CSV形式でのデータ保存
- デバッグ用のスクリーンショット・ページソース保存
- リトライ機能とエラーハンドリング

## プロジェクト構成

```
scraping-project/
├── src/
│   ├── scraper.py          # メインスクレイパークラス
│   ├── session_manager.py  # セッション・認証管理
│   ├── data_extractor.py   # データ抽出・パース
│   └── utils.py           # ユーティリティ関数
├── config/
│   └── settings.py        # 設定ファイル
├── data/                  # 取得データ保存先
├── logs/                  # ログファイル
├── screenshots/           # スクリーンショット保存先
├── page_sources/          # ページソース保存先
├── requirements.txt       # 依存パッケージ
├── investigate_site.py    # サイト調査スクリプト
└── README.md             # このファイル
```

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. ChromeDriverのインストール

Seleniumが動作するためにChromeDriverが必要です。

- [ChromeDriver公式サイト](https://chromedriver.chromium.org/)からダウンロード
- 実行可能パスに配置するか、PATHに追加

### 3. 認証情報の設定

`config/settings.py`を開き、認証情報を設定してください：

```python
CREDENTIALS = {
    "username": "your_actual_username",
    "password": "your_actual_password"
}
```

**セキュリティのため、環境変数の使用を推奨：**

```bash
export SCRAPER_USERNAME="your_username"
export SCRAPER_PASSWORD="your_password"
```

## 使用方法

### Step 1: サイト調査（必須）

実際のサイト構造を調査し、ログイン・データ取得の手順を明らかにします：

```bash
python investigate_site.py
```

調査メニュー：
1. **ログインプロセス調査** - ログインフォームの構造を分析
2. **ナビゲーション調査** - 血糖値データページへの遷移を分析
3. **データテーブル調査** - データテーブルの構造を分析

この調査結果に基づいて、各クラスのセレクターを調整してください。

### Step 2: データスクレイピング実行

```bash
cd src
python scraper.py
```

または、Pythonコードから使用：

```python
from scraper import BloodSugarScraper

# スクレイパーを初期化
scraper = BloodSugarScraper(headless=False)  # 調査時はFalse

try:
    scraper.setup_driver()
    
    # ログイン
    if scraper.login("username", "password"):
        # 血糖値データページへ遷移
        if scraper.navigate_to_blood_sugar_data():
            # データ取得（特定年月を指定可能）
            data = scraper.scrape_blood_sugar_data("2024-01")
            
            if data:
                # データ保存
                scraper.save_data(data)
                print(f"取得データ数: {len(data)}")
        
finally:
    scraper.close()
```

## 設定のカスタマイズ

### セレクター設定

`config/settings.py`の`SELECTORS`セクションで、サイト構造に応じてセレクターを調整：

```python
SELECTORS = {
    "login": {
        "username_candidates": [
            'input[name="actual_username_field"]',  # 実際のフィールド名に変更
            # ...
        ],
        "password_candidates": [
            'input[name="actual_password_field"]',  # 実際のフィールド名に変更
            # ...
        ]
    }
    # ...
}
```

### ブラウザ設定

```python
BROWSER_SETTINGS = {
    "headless": True,  # 本番運用時はTrueに設定
    "window_size": "1920,1080",
    "implicit_wait": 10
}
```

## トラブルシューティング

### よくある問題

1. **ログインに失敗する**
   - `investigate_site.py`でログインフォームの構造を再確認
   - セレクターを実際のフィールド名に合わせて調整

2. **データテーブルが見つからない**
   - データページまで手動で遷移し、テーブル構造を確認
   - キーワードやセレクターを調整

3. **ASP.NET状態エラー**
   - ViewState/EventValidationが正しく取得されているか確認
   - ページ遷移のタイミングを調整

### デバッグ機能

- **スクリーンショット保存**: 各ステップでページの状態を確認
- **ページソース保存**: HTMLソースを詳細分析
- **フォーム解析**: 入力フィールドやボタンの詳細情報を出力
- **詳細ログ**: 各処理の実行状況をログファイルに記録

## データ形式

### 出力データ例（JSON）

```json
[
  {
    "blood_sugar_value": 120.5,
    "measurement_datetime": "2024-01-15T09:30:00",
    "extracted_at": "2024-01-20T14:25:30.123456",
    "raw_data": ["120.5", "2024-01-15 09:30", "食前", "備考"]
  }
]
```

### データ保存形式

- **JSON**: 構造化されたデータとして保存（デフォルト）
- **CSV**: 表形式でデータを保存
- **バックアップ**: 自動的にバックアップファイルを作成

## 注意事項

### 法的・倫理的配慮

- **個人データ**: 血糖値データは個人の医療情報です。適切に管理してください
- **利用規約**: サイトの利用規約を遵守してください
- **アクセス頻度**: サーバーに負荷をかけないよう、適切な間隔でアクセスしてください

### セキュリティ

- 認証情報をソースコードに直接記述しないでください
- 環境変数や設定ファイルを使用してください
- データファイルのアクセス権限を適切に設定してください

## 拡張・カスタマイズ

### 新しいデータ項目の追加

`data_extractor.py`の`parse_data_table`メソッドを拡張：

```python
# 新しい列のキーワードを追加
note_col_index = self.find_column_index(headers, ["備考", "メモ", "note"])
```

### 複数月の自動取得

```python
import datetime

# 複数月のデータを取得
for month in range(1, 13):
    year_month = f"2024-{month:02d}"
    data = scraper.scrape_blood_sugar_data(year_month)
    scraper.save_data(data, f"blood_sugar_{year_month}.json")
```

## ライセンス

このプロジェクトは個人利用を目的としています。商用利用については適切なライセンスを確認してください。

## サポート

問題が発生した場合：

1. `investigate_site.py`でサイト構造を再確認
2. ログファイル（`logs/scraper.log`）を確認
3. スクリーンショットでページの状態を確認
4. 設定ファイルのセレクターを調整

---

**重要**: このツールは教育・個人利用目的で作成されています。実際の使用前に対象サイトの利用規約を確認し、適切な使用を心がけてください。
