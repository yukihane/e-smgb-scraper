"""
血糖値データ抽出・パース処理
"""
import time
import logging
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

class DataExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        
    def extract_blood_sugar_data(self, year_month=None):
        """血糖値データを抽出"""
        try:
            self.logger.info("血糖値データの抽出を開始")
            
            # 年月指定がある場合、条件を設定
            if year_month:
                if not self.set_date_filter(year_month):
                    self.logger.error("日付フィルターの設定に失敗")
                    return []
            
            # ページ内容を解析
            self.analyze_current_page()
            
            # データテーブルを探す
            data_table = self.find_data_table()
            if not data_table:
                self.logger.error("データテーブルが見つかりません")
                return []
            
            # テーブルからデータを抽出
            blood_sugar_data = self.parse_data_table(data_table)
            
            self.logger.info(f"抽出完了: {len(blood_sugar_data)}件のデータ")
            return blood_sugar_data
            
        except Exception as e:
            self.logger.error(f"データ抽出エラー: {e}")
            return []
    
    def analyze_current_page(self):
        """現在のページ構造を解析"""
        try:
            self.logger.info("ページ構造を解析中...")
            self.logger.info(f"現在のURL: {self.driver.current_url}")
            self.logger.info(f"ページタイトル: {self.driver.title}")
            
            # ページ上のテーブルを全て取得
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            self.logger.info(f"発見したテーブル数: {len(tables)}")
            
            for i, table in enumerate(tables):
                table_id = table.get_attribute("id")
                table_class = table.get_attribute("class")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.logger.info(f"テーブル{i}: id={table_id}, class={table_class}, 行数={len(rows)}")
            
            # フォーム要素を確認（日付フィルター用）
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            self.logger.info(f"発見したセレクトボックス数: {len(selects)}")
            
            for i, select in enumerate(selects):
                select_name = select.get_attribute("name")
                select_id = select.get_attribute("id")
                options = select.find_elements(By.TAG_NAME, "option")
                self.logger.info(f"セレクト{i}: name={select_name}, id={select_id}, オプション数={len(options)}")
                
        except Exception as e:
            self.logger.error(f"ページ解析エラー: {e}")
    
    def find_data_table(self):
        """血糖値データテーブルを特定"""
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            for table in tables:
                # テーブルの内容を確認して血糖値データっぽいものを探す
                table_text = table.text.lower()
                
                # 血糖値関連のキーワードを含むテーブルを探す
                blood_sugar_keywords = [
                    "血糖値", "血糖", "glucose", "mg/dl", "mmol/l",
                    "測定", "日時", "時刻", "value", "measurement"
                ]
                
                keyword_found = any(keyword in table_text for keyword in blood_sugar_keywords)
                
                if keyword_found:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:  # ヘッダー行以外にデータがある
                        self.logger.info(f"血糖値データテーブルを発見: 行数={len(rows)}")
                        return table
            
            self.logger.warning("血糖値データテーブルが見つかりませんでした")
            return None
            
        except Exception as e:
            self.logger.error(f"テーブル検索エラー: {e}")
            return None
    
    def parse_data_table(self, table):
        """テーブルからデータを解析・抽出"""
        try:
            data_list = []
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            if not rows:
                return data_list
            
            # ヘッダー行を解析して列の構造を把握
            header_row = rows[0]
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = header_row.find_elements(By.TAG_NAME, "td")
            
            headers = [cell.text.strip() for cell in header_cells]
            self.logger.info(f"テーブルヘッダー: {headers}")
            
            # 血糖値と日時の列インデックスを特定
            value_col_index = self.find_column_index(headers, ["血糖値", "glucose", "値", "value", "mg/dl"])
            datetime_col_index = self.find_column_index(headers, ["日時", "時刻", "測定日", "date", "time", "datetime"])
            
            self.logger.info(f"血糖値列: {value_col_index}, 日時列: {datetime_col_index}")
            
            # データ行を処理
            for i, row in enumerate(rows[1:], 1):  # ヘッダー行をスキップ
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < max(value_col_index or 0, datetime_col_index or 0) + 1:
                        continue
                    
                    # 血糖値を抽出
                    blood_sugar_value = None
                    if value_col_index is not None and value_col_index < len(cells):
                        value_text = cells[value_col_index].text.strip()
                        blood_sugar_value = self.extract_numeric_value(value_text)
                    
                    # 日時を抽出
                    measurement_datetime = None
                    if datetime_col_index is not None and datetime_col_index < len(cells):
                        datetime_text = cells[datetime_col_index].text.strip()
                        measurement_datetime = self.parse_datetime(datetime_text)
                    
                    # データが有効な場合のみ追加
                    if blood_sugar_value is not None:
                        data_item = {
                            "blood_sugar_value": blood_sugar_value,
                            "measurement_datetime": measurement_datetime,
                            "raw_data": [cell.text.strip() for cell in cells]  # デバッグ用
                        }
                        data_list.append(data_item)
                        
                except Exception as e:
                    self.logger.error(f"行{i}の処理エラー: {e}")
                    continue
            
            return data_list
            
        except Exception as e:
            self.logger.error(f"テーブル解析エラー: {e}")
            return []
    
    def find_column_index(self, headers, keywords):
        """指定したキーワードを含む列のインデックスを探す"""
        for i, header in enumerate(headers):
            header_lower = header.lower()
            for keyword in keywords:
                if keyword.lower() in header_lower:
                    return i
        return None
    
    def extract_numeric_value(self, text):
        """テキストから数値を抽出"""
        try:
            # 数値パターンを検索（整数または小数）
            numeric_pattern = r'(\d+\.?\d*)'
            match = re.search(numeric_pattern, text)
            
            if match:
                return float(match.group(1))
            return None
            
        except Exception as e:
            self.logger.error(f"数値抽出エラー: {text}, {e}")
            return None
    
    def parse_datetime(self, datetime_text):
        """日時文字列をパース"""
        try:
            if not datetime_text:
                return None
            
            # よくある日時フォーマットのパターン
            datetime_patterns = [
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M',
                '%m/%d/%Y',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M',
                '%d/%m/%Y'
            ]
            
            for pattern in datetime_patterns:
                try:
                    parsed_datetime = datetime.strptime(datetime_text, pattern)
                    return parsed_datetime.isoformat()
                except ValueError:
                    continue
            
            self.logger.warning(f"日時パースに失敗: {datetime_text}")
            return datetime_text  # パースできない場合は元の文字列を返す
            
        except Exception as e:
            self.logger.error(f"日時パースエラー: {e}")
            return None
    
    def set_date_filter(self, year_month):
        """年月フィルターを設定"""
        try:
            self.logger.info(f"日付フィルターを設定: {year_month}")
            
            # year_monthの形式は "YYYY-MM" を想定
            year, month = year_month.split('-')
            
            # 年のセレクトボックスを探す
            year_selects = self.find_select_elements(['year', '年', 'yyyy'])
            if year_selects:
                year_select = Select(year_selects[0])
                try:
                    year_select.select_by_value(year)
                    self.logger.info(f"年を設定: {year}")
                except:
                    year_select.select_by_visible_text(year)
            
            # 月のセレクトボックスを探す
            month_selects = self.find_select_elements(['month', '月', 'mm'])
            if month_selects:
                month_select = Select(month_selects[0])
                try:
                    month_select.select_by_value(month)
                    self.logger.info(f"月を設定: {month}")
                except:
                    month_select.select_by_visible_text(month)
            
            # フィルター適用ボタンを探してクリック
            filter_buttons = self.driver.find_elements(By.XPATH, 
                "//input[@type='submit' or @type='button'][@value[contains(., '検索') or contains(., '表示') or contains(., 'Search') or contains(., 'Filter')]]")
            
            if filter_buttons:
                filter_buttons[0].click()
                time.sleep(3)  # フィルター適用の待機
                self.logger.info("フィルターを適用しました")
                return True
            
            return True  # フィルターボタンがなくても、セレクトボックスの設定だけで十分な場合もある
            
        except Exception as e:
            self.logger.error(f"日付フィルター設定エラー: {e}")
            return False
    
    def find_select_elements(self, keywords):
        """指定したキーワードを含むセレクト要素を探す"""
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        matching_selects = []
        
        for select in selects:
            select_name = (select.get_attribute("name") or "").lower()
            select_id = (select.get_attribute("id") or "").lower()
            
            for keyword in keywords:
                if keyword.lower() in select_name or keyword.lower() in select_id:
                    matching_selects.append(select)
                    break
        
        return matching_selects
