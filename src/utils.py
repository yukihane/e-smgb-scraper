"""
ユーティリティ関数・クラス
"""
import time
import json
import csv
import os
import logging
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Utils:
    @staticmethod
    def setup_directories():
        """必要なディレクトリを作成"""
        directories = [
            "../data",
            "../data/backup", 
            "../logs",
            "../screenshots",
            "../page_sources"
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"ディレクトリを作成: {directory}")
    
    @staticmethod
    def save_data_as_json(data, filename=None):
        """データをJSON形式で保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blood_sugar_data_{timestamp}.json"
        
        filepath = f"../data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    @staticmethod
    def save_data_as_csv(data, filename=None):
        """データをCSV形式で保存"""
        if not data:
            return None
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blood_sugar_data_{timestamp}.csv"
        
        filepath = f"../data/{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
    
    @staticmethod
    def create_backup(filepath):
        """データファイルのバックアップを作成"""
        if os.path.exists(filepath):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}_{os.path.basename(filepath)}"
            backup_path = f"../data/backup/{backup_name}"
            
            import shutil
            shutil.copy2(filepath, backup_path)
            return backup_path
        return None

class DebugUtils:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
    
    def save_screenshot(self, filename=None):
        """スクリーンショットを保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = f"../screenshots/{filename}"
        self.driver.save_screenshot(filepath)
        self.logger.info(f"スクリーンショットを保存: {filepath}")
        return filepath
    
    def save_page_source(self, filename=None):
        """ページソースを保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_source_{timestamp}.html"
        
        filepath = f"../page_sources/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        
        self.logger.info(f"ページソースを保存: {filepath}")
        return filepath
    
    def analyze_form_elements(self):
        """フォーム要素を詳細に解析"""
        analysis = {
            "inputs": [],
            "selects": [],
            "buttons": [],
            "forms": []
        }
        
        # input要素
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for input_elem in inputs:
            input_info = {
                "type": input_elem.get_attribute("type"),
                "name": input_elem.get_attribute("name"),
                "id": input_elem.get_attribute("id"),
                "class": input_elem.get_attribute("class"),
                "value": input_elem.get_attribute("value"),
                "placeholder": input_elem.get_attribute("placeholder")
            }
            analysis["inputs"].append(input_info)
        
        # select要素
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for select_elem in selects:
            options = select_elem.find_elements(By.TAG_NAME, "option")
            select_info = {
                "name": select_elem.get_attribute("name"),
                "id": select_elem.get_attribute("id"),
                "class": select_elem.get_attribute("class"),
                "options": [{"value": opt.get_attribute("value"), "text": opt.text} for opt in options]
            }
            analysis["selects"].append(select_info)
        
        # button要素
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button_elem in buttons:
            button_info = {
                "type": button_elem.get_attribute("type"),
                "name": button_elem.get_attribute("name"),
                "id": button_elem.get_attribute("id"),
                "class": button_elem.get_attribute("class"),
                "text": button_elem.text
            }
            analysis["buttons"].append(button_info)
        
        # form要素
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        for form_elem in forms:
            form_info = {
                "action": form_elem.get_attribute("action"),
                "method": form_elem.get_attribute("method"),
                "name": form_elem.get_attribute("name"),
                "id": form_elem.get_attribute("id"),
                "class": form_elem.get_attribute("class")
            }
            analysis["forms"].append(form_info)
        
        return analysis
    
    def save_form_analysis(self, analysis, filename=None):
        """フォーム解析結果を保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"form_analysis_{timestamp}.json"
        
        filepath = f"../data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"フォーム解析結果を保存: {filepath}")
        return filepath

class RetryUtils:
    @staticmethod
    def retry_on_exception(func, max_retries=3, delay=5, exceptions=(Exception,)):
        """例外発生時にリトライを行う"""
        for attempt in range(max_retries):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"リトライ {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay)
        return None
    
    @staticmethod
    def wait_for_element_with_retry(driver, by, value, timeout=10, max_retries=3):
        """要素の出現を待機（リトライ付き）"""
        for attempt in range(max_retries):
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"要素待機リトライ {attempt + 1}/{max_retries}: {value}")
                time.sleep(2)
        return None

class DataProcessor:
    @staticmethod
    def clean_data(raw_data):
        """生データをクリーニング"""
        cleaned_data = []
        
        for item in raw_data:
            if not item.get("blood_sugar_value"):
                continue
                
            cleaned_item = {
                "blood_sugar_value": item.get("blood_sugar_value"),
                "measurement_datetime": item.get("measurement_datetime"),
                "extracted_at": datetime.now().isoformat()
            }
            
            # 必要に応じて追加フィールドを処理
            if item.get("raw_data"):
                cleaned_item["raw_data"] = item["raw_data"]
            
            cleaned_data.append(cleaned_item)
        
        return cleaned_data
    
    @staticmethod
    def validate_data(data):
        """データの妥当性をチェック"""
        validation_results = {
            "total_records": len(data),
            "valid_records": 0,
            "invalid_records": 0,
            "errors": []
        }
        
        for i, item in enumerate(data):
            is_valid = True
            
            # 血糖値の妥当性チェック
            blood_sugar = item.get("blood_sugar_value")
            if not blood_sugar or not isinstance(blood_sugar, (int, float)):
                validation_results["errors"].append(f"Record {i}: Invalid blood sugar value")
                is_valid = False
            elif blood_sugar < 0 or blood_sugar > 1000:  # 常識的な範囲チェック
                validation_results["errors"].append(f"Record {i}: Blood sugar value out of range: {blood_sugar}")
                is_valid = False
            
            if is_valid:
                validation_results["valid_records"] += 1
            else:
                validation_results["invalid_records"] += 1
        
        return validation_results
    
    @staticmethod
    def generate_summary(data):
        """データのサマリーを生成"""
        if not data:
            return {"message": "No data to summarize"}
        
        blood_sugar_values = [item["blood_sugar_value"] for item in data if item.get("blood_sugar_value")]
        
        if not blood_sugar_values:
            return {"message": "No valid blood sugar values found"}
        
        summary = {
            "total_measurements": len(blood_sugar_values),
            "average": sum(blood_sugar_values) / len(blood_sugar_values),
            "minimum": min(blood_sugar_values),
            "maximum": max(blood_sugar_values),
            "date_range": {
                "earliest": min([item.get("measurement_datetime") for item in data if item.get("measurement_datetime")], default=None),
                "latest": max([item.get("measurement_datetime") for item in data if item.get("measurement_datetime")], default=None)
            }
        }
        
        return summary
