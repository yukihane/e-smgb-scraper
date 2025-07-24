"""
スクレイピング設定ファイル
"""

# 基本設定
BASE_URL = "https://cloud.e-smbg.net/"

# ブラウザ設定
BROWSER_SETTINGS = {
    "headless": False,  # 調査時はFalseに設定
    "window_size": "1920,1080",
    "implicit_wait": 10,
    "page_load_timeout": 30
}

# ログ設定
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "log_file": "../logs/scraper.log"
}

# リクエスト設定
REQUEST_SETTINGS = {
    "delay_between_requests": 2,  # リクエスト間の待機時間（秒）
    "retry_count": 3,  # リトライ回数
    "retry_delay": 5  # リトライ間の待機時間（秒）
}

# データ保存設定
DATA_SETTINGS = {
    "output_directory": "../data",
    "backup_directory": "../data/backup",
    "default_format": "json",  # json, csv
    "include_raw_data": True  # デバッグ用の生データを含めるか
}

# ASP.NET特有の設定
ASPNET_SETTINGS = {
    "viewstate_param": "__VIEWSTATE",
    "eventvalidation_param": "__EVENTVALIDATION",
    "dopostback_param": "__DOPOSTBACK",
    "eventtarget_param": "__EVENTTARGET",
    "scroll_param": "__SCROLL"
}

# セレクター設定（実際のサイト構造に応じて調整）
SELECTORS = {
    # ログインフォーム
    "login": {
        "username_candidates": [
            'input[name*="user"]', 'input[id*="user"]',
            'input[name*="User"]', 'input[id*="User"]',
            'input[name*="login"]', 'input[id*="login"]',
            'input[name*="Login"]', 'input[id*="Login"]',
            'input[name*="id"]', 'input[id*="id"]',
            'input[type="text"]'
        ],
        "password_candidates": [
            'input[name*="pass"]', 'input[id*="pass"]',
            'input[name*="Pass"]', 'input[id*="Pass"]',
            'input[name*="password"]', 'input[id*="password"]',
            'input[name*="Password"]', 'input[id*="Password"]',
            'input[type="password"]'
        ],
        "submit_candidates": [
            'input[type="submit"]',
            'button[type="submit"]',
            'input[value*="ログイン"]',
            'input[value*="Login"]',
            'button[name*="login"]',
            'button[id*="login"]'
        ]
    },
    
    # データテーブル
    "data_table": {
        "table_keywords": [
            "血糖値", "血糖", "glucose", "mg/dl", "mmol/l",
            "測定", "日時", "時刻", "value", "measurement"
        ],
        "value_column_keywords": [
            "血糖値", "glucose", "値", "value", "mg/dl"
        ],
        "datetime_column_keywords": [
            "日時", "時刻", "測定日", "date", "time", "datetime"
        ]
    },
    
    # ナビゲーション
    "navigation": {
        "link_keywords": [
            "血糖値", "血糖", "データ", "記録", "履歴", "測定値",
            "Blood Sugar", "Data", "Records", "History", "Measurements"
        ]
    },
    
    # 日付フィルター
    "date_filter": {
        "year_keywords": ["year", "年", "yyyy"],
        "month_keywords": ["month", "月", "mm"],
        "filter_button_keywords": ["検索", "表示", "Search", "Filter"]
    }
}

# デバッグ設定
DEBUG_SETTINGS = {
    "save_page_source": True,  # ページソースを保存するか
    "save_screenshots": True,  # スクリーンショットを保存するか
    "verbose_logging": True,  # 詳細ログを出力するか
    "analyze_page_structure": True  # ページ構造を解析するか
}

# ユーザー認証情報（実際の値に置き換えてください）
# セキュリティのため、環境変数から読み込むことを推奨
import os

CREDENTIALS = {
    "username": os.getenv("SCRAPER_USERNAME", "your_username"),
    "password": os.getenv("SCRAPER_PASSWORD", "your_password")
}
