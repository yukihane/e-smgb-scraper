"""
血糖値データスクレイピングメインクラス
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from session_manager import SessionManager
from data_extractor import DataExtractor
import json

class BloodSugarScraper:
    def __init__(self, headless=False):
        self.setup_logging()
        self.headless = headless
        self.driver = None
        self.session_manager = None
        self.data_extractor = None
        
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Selenium WebDriverセットアップ"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # セッションマネージャーとデータ抽出器を初期化
        self.session_manager = SessionManager(self.driver)
        self.data_extractor = DataExtractor(self.driver)
        
    def login(self, username, password):
        """ログイン処理"""
        try:
            self.logger.info("ログイン処理を開始")
            return self.session_manager.login(username, password)
        except Exception as e:
            self.logger.error(f"ログインエラー: {e}")
            return False
    
    def navigate_to_blood_sugar_data(self):
        """血糖値データ一覧ページへ遷移"""
        try:
            self.logger.info("血糖値データページへ遷移")
            return self.session_manager.navigate_to_data_page()
        except Exception as e:
            self.logger.error(f"ページ遷移エラー: {e}")
            return False
    
    def scrape_blood_sugar_data(self, year_month=None):
        """血糖値データをスクレイピング"""
        try:
            self.logger.info(f"血糖値データ取得開始: {year_month}")
            return self.data_extractor.extract_blood_sugar_data(year_month)
        except Exception as e:
            self.logger.error(f"データ取得エラー: {e}")
            return []
    
    def save_data(self, data, filename=None):
        """データを保存"""
        if not filename:
            filename = f"blood_sugar_data_{int(time.time())}.json"
        
        filepath = f"../data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"データを保存しました: {filepath}")
    
    def close(self):
        """リソースクリーンアップ"""
        if self.driver:
            self.driver.quit()
            self.logger.info("ドライバーを終了しました")

if __name__ == "__main__":
    # 使用例
    scraper = BloodSugarScraper(headless=False)  # 調査時はheadless=False
    
    try:
        scraper.setup_driver()
        
        # ログイン情報（実際の値に置き換えてください）
        username = "your_username"
        password = "your_password"
        
        if scraper.login(username, password):
            if scraper.navigate_to_blood_sugar_data():
                data = scraper.scrape_blood_sugar_data()
                if data:
                    scraper.save_data(data)
                    print(f"取得データ数: {len(data)}")
                else:
                    print("データが取得できませんでした")
            else:
                print("血糖値データページへの遷移に失敗しました")
        else:
            print("ログインに失敗しました")
            
    finally:
        scraper.close()
