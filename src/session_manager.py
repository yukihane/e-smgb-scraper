"""
ASP.NETセッション管理とログイン処理
"""
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

class SessionManager:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://cloud.e-smbg.net/"
        self.viewstate = None
        self.eventvalidation = None
        
    def get_aspnet_params(self):
        """ASP.NET状態パラメータを取得"""
        try:
            # __VIEWSTATE
            viewstate_element = self.driver.find_element(By.NAME, "__VIEWSTATE")
            self.viewstate = viewstate_element.get_attribute("value")
            
            # __EVENTVALIDATION
            try:
                eventvalidation_element = self.driver.find_element(By.NAME, "__EVENTVALIDATION")
                self.eventvalidation = eventvalidation_element.get_attribute("value")
            except:
                self.eventvalidation = None
                
            self.logger.info("ASP.NET状態パラメータを取得しました")
            return True
        except Exception as e:
            self.logger.error(f"ASP.NET状態パラメータ取得エラー: {e}")
            return False
    
    def login(self, username, password):
        """ログイン処理"""
        try:
            self.logger.info("ログインページにアクセス")
            self.driver.get(self.base_url)
            
            # ページの読み込み待機
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # ログインフォームの要素を探す（実際のサイト構造に応じて調整が必要）
            # まずはページの内容をログに出力して構造を確認
            self.logger.info(f"現在のURL: {self.driver.current_url}")
            self.logger.info(f"ページタイトル: {self.driver.title}")
            
            # ASP.NET状態パラメータを取得
            self.get_aspnet_params()
            
            # ログインフィールドを特定（セレクタは実際のサイトに合わせて調整）
            try:
                # よくあるIDやname属性のパターンを試す
                username_field = None
                password_field = None
                
                # ユーザー名フィールドを探す
                possible_username_selectors = [
                    'input[name*="user"]', 'input[id*="user"]',
                    'input[name*="User"]', 'input[id*="User"]',
                    'input[name*="login"]', 'input[id*="login"]',
                    'input[name*="Login"]', 'input[id*="Login"]',
                    'input[name*="id"]', 'input[id*="id"]',
                    'input[type="text"]'
                ]
                
                for selector in possible_username_selectors:
                    try:
                        username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        self.logger.info(f"ユーザー名フィールドを発見: {selector}")
                        break
                    except:
                        continue
                
                # パスワードフィールドを探す
                possible_password_selectors = [
                    'input[name*="pass"]', 'input[id*="pass"]',
                    'input[name*="Pass"]', 'input[id*="Pass"]',
                    'input[name*="password"]', 'input[id*="password"]',
                    'input[name*="Password"]', 'input[id*="Password"]',
                    'input[type="password"]'
                ]
                
                for selector in possible_password_selectors:
                    try:
                        password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        self.logger.info(f"パスワードフィールドを発見: {selector}")
                        break
                    except:
                        continue
                
                if not username_field or not password_field:
                    # フォーム要素が見つからない場合、ページのHTMLを取得して分析
                    self.analyze_page_structure()
                    return False
                
                # 認証情報を入力
                username_field.clear()
                username_field.send_keys(username)
                
                password_field.clear()
                password_field.send_keys(password)
                
                # ログインボタンを探す
                login_button = None
                possible_button_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'input[value*="ログイン"]',
                    'input[value*="Login"]',
                    'button[name*="login"]',
                    'button[id*="login"]'
                ]
                
                for selector in possible_button_selectors:
                    try:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        self.logger.info(f"ログインボタンを発見: {selector}")
                        break
                    except:
                        continue
                
                if login_button:
                    login_button.click()
                else:
                    # ボタンが見つからない場合、Enterキーでフォーム送信を試す
                    from selenium.webdriver.common.keys import Keys
                    password_field.send_keys(Keys.RETURN)
                
                # ログイン後のページ遷移を待機
                time.sleep(3)
                
                # ログイン成功の判定（URL変化やページ内容で判断）
                current_url = self.driver.current_url
                if current_url != self.base_url and "login" not in current_url.lower():
                    self.logger.info("ログインに成功しました")
                    return True
                else:
                    self.logger.error("ログインに失敗した可能性があります")
                    return False
                    
            except Exception as e:
                self.logger.error(f"ログイン処理中のエラー: {e}")
                self.analyze_page_structure()
                return False
                
        except Exception as e:
            self.logger.error(f"ログインエラー: {e}")
            return False
    
    def analyze_page_structure(self):
        """ページ構造を解析してログに出力"""
        try:
            # 入力フィールドを全て取得
            input_fields = self.driver.find_elements(By.TAG_NAME, "input")
            self.logger.info(f"発見した入力フィールド数: {len(input_fields)}")
            
            for i, field in enumerate(input_fields):
                field_type = field.get_attribute("type")
                field_name = field.get_attribute("name")
                field_id = field.get_attribute("id")
                field_value = field.get_attribute("value")
                self.logger.info(f"フィールド{i}: type={field_type}, name={field_name}, id={field_id}, value={field_value}")
            
            # ボタンを全て取得
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            submit_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
            
            self.logger.info(f"発見したボタン数: {len(buttons + submit_inputs)}")
            
            for i, button in enumerate(buttons + submit_inputs):
                button_text = button.text or button.get_attribute("value")
                button_name = button.get_attribute("name")
                button_id = button.get_attribute("id")
                self.logger.info(f"ボタン{i}: text={button_text}, name={button_name}, id={button_id}")
                
        except Exception as e:
            self.logger.error(f"ページ構造解析エラー: {e}")
    
    def navigate_to_data_page(self):
        """血糖値データページへ遷移"""
        try:
            self.logger.info("血糖値データページへの遷移を開始")
            
            # 現在のページでナビゲーションメニューを探す
            # 実際のサイト構造に応じて調整が必要
            
            # よくあるリンクテキストやセレクタのパターンを試す
            possible_link_texts = [
                "血糖値", "血糖", "データ", "記録", "履歴", "測定値",
                "Blood Sugar", "Data", "Records", "History", "Measurements"
            ]
            
            navigation_found = False
            
            for link_text in possible_link_texts:
                try:
                    # テキストを含むリンクを探す
                    links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, link_text)
                    if links:
                        self.logger.info(f"リンクを発見: {link_text}")
                        links[0].click()
                        navigation_found = True
                        break
                except:
                    continue
            
            if not navigation_found:
                # メニュー項目をクラス名やIDで探す
                self.analyze_navigation_menu()
                return False
            
            # ページ遷移の待機
            time.sleep(3)
            
            # ASP.NET状態パラメータを更新
            self.get_aspnet_params()
            
            self.logger.info("血糖値データページへの遷移完了")
            return True
            
        except Exception as e:
            self.logger.error(f"ページ遷移エラー: {e}")
            return False
    
    def analyze_navigation_menu(self):
        """ナビゲーションメニューを解析"""
        try:
            # すべてのリンクを取得
            links = self.driver.find_elements(By.TAG_NAME, "a")
            self.logger.info(f"発見したリンク数: {len(links)}")
            
            for i, link in enumerate(links):
                link_text = link.text.strip()
                link_href = link.get_attribute("href")
                if link_text:  # 空のテキストは除外
                    self.logger.info(f"リンク{i}: text='{link_text}', href='{link_href}'")
                    
        except Exception as e:
            self.logger.error(f"ナビゲーション解析エラー: {e}")
