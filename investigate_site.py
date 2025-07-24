"""
サイト調査用スクリプト
実際のサイトにアクセスして構造を調査し、ログイン・データ取得の手順を明らかにする
"""

import sys
import os
import time

# srcディレクトリをパスに追加
sys.path.append('src')

from scraper import BloodSugarScraper
from utils import Utils, DebugUtils
from config.settings import CREDENTIALS, DEBUG_SETTINGS

def investigate_login_process():
    """ログインプロセスを調査"""
    print("=== ログインプロセス調査開始 ===")
    
    # 必要なディレクトリを作成
    Utils.setup_directories()
    
    scraper = BloodSugarScraper(headless=False)
    
    try:
        scraper.setup_driver()
        debug_utils = DebugUtils(scraper.driver)
        
        # ログインページにアクセス
        print("1. ログインページにアクセス中...")
        scraper.driver.get("https://cloud.e-smbg.net/")
        time.sleep(3)
        
        # 初期ページのスクリーンショットを保存
        debug_utils.save_screenshot("01_initial_page.png")
        debug_utils.save_page_source("01_initial_page.html")
        
        # フォーム要素を解析
        print("2. フォーム要素を解析中...")
        form_analysis = debug_utils.analyze_form_elements()
        debug_utils.save_form_analysis(form_analysis, "01_login_form_analysis.json")
        
        # ログインフィールドの詳細を表示
        print("\n=== 発見したINPUT要素 ===")
        for i, input_elem in enumerate(form_analysis["inputs"]):
            print(f"Input {i}: type={input_elem['type']}, name={input_elem['name']}, id={input_elem['id']}")
            if input_elem['placeholder']:
                print(f"  placeholder: {input_elem['placeholder']}")
        
        print("\n=== 発見したBUTTON要素 ===")
        for i, button_elem in enumerate(form_analysis["buttons"]):
            print(f"Button {i}: type={button_elem['type']}, name={button_elem['name']}, id={button_elem['id']}, text={button_elem['text']}")
        
        print("\n=== 発見したFORM要素 ===")
        for i, form_elem in enumerate(form_analysis["forms"]):
            print(f"Form {i}: action={form_elem['action']}, method={form_elem['method']}")
        
        # 手動でログイン情報を入力するための待機
        print("\n3. 手動でログイン情報を入力してください...")
        print("   - ユーザー名とパスワードを入力")
        print("   - まだログインボタンは押さないでください")
        input("入力完了後、Enterキーを押してください...")
        
        # ログイン情報入力後のスクリーンショット
        debug_utils.save_screenshot("02_login_filled.png")
        
        print("4. ログインボタンをクリックしてください...")
        input("ログイン完了後、Enterキーを押してください...")
        
        # ログイン後のページ
        debug_utils.save_screenshot("03_after_login.png")
        debug_utils.save_page_source("03_after_login.html")
        
        print(f"ログイン後のURL: {scraper.driver.current_url}")
        print(f"ページタイトル: {scraper.driver.title}")
        
        return True
        
    except Exception as e:
        print(f"調査中にエラーが発生: {e}")
        return False
    finally:
        print("ブラウザを開いたままにします。調査完了後、手動で閉じてください。")
        input("調査を終了するにはEnterキーを押してください...")
        scraper.close()

def investigate_navigation():
    """ナビゲーション調査"""
    print("\n=== ナビゲーション調査開始 ===")
    
    scraper = BloodSugarScraper(headless=False)
    
    try:
        scraper.setup_driver()
        debug_utils = DebugUtils(scraper.driver)
        
        # まずログインページにアクセス
        print("1. ログインしてください...")
        scraper.driver.get("https://cloud.e-smbg.net/")
        input("ログイン完了後、Enterキーを押してください...")
        
        # ログイン後のページを解析
        print("2. ログイン後のページを解析中...")
        debug_utils.save_screenshot("04_logged_in_page.png")
        debug_utils.save_page_source("04_logged_in_page.html")
        
        # すべてのリンクを解析
        from selenium.webdriver.common.by import By
        links = scraper.driver.find_elements(By.TAG_NAME, "a")
        print(f"\n=== 発見したリンク（{len(links)}個） ===")
        for i, link in enumerate(links):
            href = link.get_attribute("href")
            text = link.text.strip()
            if text:  # 空のテキストは除外
                print(f"Link {i}: '{text}' -> {href}")
        
        print("\n3. 血糖値データに関連しそうなリンクをクリックしてください...")
        input("ページ遷移後、Enterキーを押してください...")
        
        # 遷移後のページ
        debug_utils.save_screenshot("05_data_page.png")
        debug_utils.save_page_source("05_data_page.html")
        
        print(f"遷移後のURL: {scraper.driver.current_url}")
        print(f"ページタイトル: {scraper.driver.title}")
        
        return True
        
    except Exception as e:
        print(f"ナビゲーション調査中にエラーが発生: {e}")
        return False
    finally:
        input("調査を終了するにはEnterキーを押してください...")
        scraper.close()

def investigate_data_table():
    """データテーブル調査"""
    print("\n=== データテーブル調査開始 ===")
    
    scraper = BloodSugarScraper(headless=False)
    
    try:
        scraper.setup_driver()
        debug_utils = DebugUtils(scraper.driver)
        
        print("1. 血糖値データが表示されるページまで手動で遷移してください...")
        scraper.driver.get("https://cloud.e-smbg.net/")
        input("血糖値データが表示されているページで、Enterキーを押してください...")
        
        # データページのスクリーンショット
        debug_utils.save_screenshot("06_blood_sugar_data.png")
        debug_utils.save_page_source("06_blood_sugar_data.html")
        
        print("2. テーブル構造を解析中...")
        
        # テーブルを全て取得
        from selenium.webdriver.common.by import By
        tables = scraper.driver.find_elements(By.TAG_NAME, "table")
        print(f"発見したテーブル数: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\n=== テーブル {i} ===")
            table_id = table.get_attribute("id")
            table_class = table.get_attribute("class")
            print(f"ID: {table_id}, Class: {table_class}")
            
            # 行を取得
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"行数: {len(rows)}")
            
            # 最初の数行を表示
            for j, row in enumerate(rows[:5]):  # 最初の5行のみ表示
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:  # tdがない場合はthを探す
                    cells = row.find_elements(By.TAG_NAME, "th")
                
                cell_texts = [cell.text.strip() for cell in cells]
                print(f"  行{j}: {cell_texts}")
        
        # フォーム要素も解析（日付フィルター用）
        print("\n3. フォーム要素を解析中...")
        form_analysis = debug_utils.analyze_form_elements()
        
        print("\n=== SELECT要素（日付フィルター用） ===")
        for i, select_elem in enumerate(form_analysis["selects"]):
            print(f"Select {i}: name={select_elem['name']}, id={select_elem['id']}")
            print(f"  オプション: {[opt['text'] for opt in select_elem['options'][:10]]}")  # 最初の10個のみ表示
        
        debug_utils.save_form_analysis(form_analysis, "06_data_page_form_analysis.json")
        
        return True
        
    except Exception as e:
        print(f"データテーブル調査中にエラーが発生: {e}")
        return False
    finally:
        input("調査を終了するにはEnterキーを押してください...")
        scraper.close()

def main():
    """メイン調査プロセス"""
    print("血糖値データスクレイピング - サイト調査ツール")
    print("=" * 50)
    
    while True:
        print("\n調査メニュー:")
        print("1. ログインプロセス調査")
        print("2. ナビゲーション調査")
        print("3. データテーブル調査")
        print("4. 全て実行")
        print("0. 終了")
        
        choice = input("\n選択してください (0-4): ").strip()
        
        if choice == "0":
            print("調査を終了します。")
            break
        elif choice == "1":
            investigate_login_process()
        elif choice == "2":
            investigate_navigation()
        elif choice == "3":
            investigate_data_table()
        elif choice == "4":
            investigate_login_process()
            investigate_navigation()
            investigate_data_table()
        else:
            print("無効な選択です。")

if __name__ == "__main__":
    main()
