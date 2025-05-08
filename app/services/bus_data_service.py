import logging
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json
from flask import current_app
from app.models.bus_info import BusInfo
from app import db

logger = logging.getLogger(__name__)

class BusDataService:
    """Service for fetching bus data from dynamic JavaScript-based website"""
    
    def __init__(self):
        self.source = "野崎"
        self.destinations = {
            "三鷹駅": {"url_suffix": "bus.htm?tabName=searchTab&from=%E9%87%8E%E5%B4%8E&to=%E4%B8%89%E9%B7%B9%E9%A7%85&toType=1&locale=ja"},
            "吉祥寺駅": {"url_suffix": "bus.htm?tabName=searchTab&from=%E9%87%8E%E5%B4%8E&to=%E5%90%89%E7%A5%A5%E5%AF%BA%E9%A7%85&toType=1&locale=ja"},
            "武蔵境駅南口": {"url_suffix": "bus.htm?tabName=searchTab&from=%E9%87%8E%E5%B4%8E&to=%E6%AD%A6%E8%94%B5%E5%A2%83%E9%A7%85%E5%8D%97%E5%8F%A3&toType=1&locale=ja"},
            "調布駅北口": {"url_suffix": "bus.htm?tabName=searchTab&from=%E9%87%8E%E5%B4%8E&to=%E8%AA%BF%E5%B8%83%E9%A7%85%E5%8C%97%E5%8F%A3&toType=1&locale=ja"}
        }
        self.base_url = "https://odakyu.bus-navigation.jp/wgsys/wgp"
        self.retry_count = 3
        self.page_load_timeout = 30  # seconds
        self.element_wait_timeout = 20  # seconds
        
        # API関連（将来的な実装用）
        self.api_available = False
        self.api_endpoint = None
        self.api_key = None
    
    def _setup_webdriver(self):
        """
        Seleniumのwebdriverをセットアップ
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Docker環境でのパス
            driver_path = '/usr/bin/chromedriver'
            service = Service(driver_path)
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(self.page_load_timeout)
            return driver
        except Exception as e:
            logger.error(f"Webdriverのセットアップに失敗しました: {str(e)}")
            raise
    
    def fetch_all_bus_data(self):
        """
        すべての目的地のバスデータを取得
        """
        logger.info("全目的地のバスデータ取得を開始します")
        
        # 現在のデータを非アクティブ化
        BusInfo.deactivate_all()
        
        success_count = 0
        driver = None
        
        try:
            # 公式APIが利用可能か最初に確認
            if self.api_available and self.api_endpoint:
                logger.info("公式APIを使用してデータを取得します")
                success_count = self._fetch_all_from_api()
            else:
                # APIが利用できない場合はSeleniumでスクレイピング
                logger.info("Seleniumを使用してデータを取得します")
                driver = self._setup_webdriver()
                
                # 各目的地のデータを取得
                for destination, config in self.destinations.items():
                    try:
                        logger.info(f"目的地のデータを取得します: {destination}")
                        if self._fetch_destination_data_with_selenium(driver, destination, config):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"{destination}のデータ取得エラー: {str(e)}")
        except Exception as e:
            logger.error(f"バスデータ取得中のエラー: {str(e)}")
        finally:
            # ドライバーを閉じる
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        logger.info(f"バスデータ取得完了。{success_count}/{len(self.destinations)}の目的地を更新しました")
        
        return success_count == len(self.destinations)
    
    def _fetch_all_from_api(self):
        """
        公式APIからすべての目的地のデータを取得（将来的な実装用）
        """
        # この部分は公式APIが提供された場合に実装
        logger.info("公式API取得機能は未実装です")
        return 0
    
    def _fetch_destination_data_with_selenium(self, driver, destination, config):
        """
        特定の目的地のバスデータをSeleniumを使って取得
        """
        url = f"{self.base_url}/{config['url_suffix']}"
        
        # リトライロジック
        for attempt in range(self.retry_count):
            try:
                logger.info(f"URL {url} にアクセスします（試行 {attempt+1}/{self.retry_count}）")
                driver.get(url)
                
                # ページが完全に読み込まれるまで待機
                logger.info("ページの読み込みを待機しています...")
                
                # JavaScriptによる動的読み込みを待機
                try:
                    # バス情報コンテナの要素が読み込まれるまで待機
                    WebDriverWait(driver, self.element_wait_timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".route-result-list"))
                    )
                    
                    # さらに少し待機してJavaScriptの処理を確実に完了させる
                    time.sleep(3)
                    
                    logger.info("ページが完全に読み込まれました")
                except TimeoutException:
                    logger.warning("ページ要素の待機中にタイムアウトしました")
                    if attempt == self.retry_count - 1:
                        raise
                    continue  # 次のリトライへ
                
                # ページのHTMLを取得し処理
                page_source = driver.page_source
                self._process_html_response(destination, page_source)
                return True
                
            except (WebDriverException, Exception) as e:
                logger.warning(f"試行 {attempt+1}/{self.retry_count} が失敗しました: {str(e)}")
                if attempt == self.retry_count - 1:
                    raise
                
                # 一時停止してから再試行
                time.sleep(2)
        
        return False
    
    def _process_html_response(self, destination, html_content):
        """
        バス情報ウェブサイトからのHTML内容を処理
        
        注: 実際のウェブサイト構造に基づいたセレクタが必要になります
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # バスエントリーを探す
            # 実際のサイト構造に基づいて更新が必要です
            # 例: route-result-list内のroute-itemなど
            bus_entries = soup.select('.route-result-item')
            
            if not bus_entries:
                logger.warning(f"{destination}のバス情報が見つかりませんでした")
                return False
            
            logger.info(f"{len(bus_entries)}件のバス情報が見つかりました")
            
            # 各バスエントリーを処理
            for i, entry in enumerate(bus_entries[:3]):  # 最初の3件のみ処理
                try:
                    # バス番号を抽出 (例: "鷹52")
                    # 実際のセレクタを調整する必要があります
                    bus_number_elem = entry.select_one('.route-no, .bus-number')
                    bus_number = bus_number_elem.text.strip() if bus_number_elem else "不明"
                    
                    # 停留所番号
                    stop_number_elem = entry.select_one('.stop-number, .platform-number')
                    stop_number = stop_number_elem.text.strip() if stop_number_elem else "1"
                    
                    # 発車予定時刻
                    departure_elem = entry.select_one('.departure-time, .start-time')
                    departure_time_str = departure_elem.text.strip() if departure_elem else ""
                    
                    # 到着予定時刻
                    arrival_elem = entry.select_one('.arrival-time, .end-time')
                    arrival_time_str = arrival_elem.text.strip() if arrival_elem else ""
                    
                    # 発車までの残り時間
                    remaining_elem = entry.select_one('.remaining-time, .time-left')
                    remaining_text = remaining_elem.text.strip() if remaining_elem else ""
                    
                    # 残り時間から分数を抽出
                    minutes_match = re.search(r'(\d+)分', remaining_text)
                    estimated_minutes = int(minutes_match.group(1)) if minutes_match else None
                    
                    # 現在時刻から時間を計算
                    now = datetime.now()
                    
                    # 発車予定時刻を解析
                    scheduled_departure = None
                    if departure_time_str:
                        try:
                            # "HH:MM" 形式を解析
                            hour, minute = map(int, departure_time_str.split(':'))
                            scheduled_departure = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            
                            # 日付をまたぐ場合の処理 (現在時刻より前なら翌日と判断)
                            if scheduled_departure < now:
                                scheduled_departure = scheduled_departure + timedelta(days=1)
                        except Exception as e:
                            logger.warning(f"発車時刻の解析に失敗しました: {departure_time_str}, エラー: {str(e)}")
                            scheduled_departure = now + timedelta(minutes=30)  # フォールバック
                    else:
                        scheduled_departure = now + timedelta(minutes=30)  # 時刻不明の場合のダミーデータ
                    
                    # 予測発車時刻を計算
                    predicted_departure = None
                    if estimated_minutes is not None:
                        predicted_departure = now + timedelta(minutes=estimated_minutes)
                    else:
                        predicted_departure = scheduled_departure  # 推定時間がなければ予定時刻を使用
                    
                    # 到着予定時刻を解析
                    scheduled_arrival = None
                    if arrival_time_str:
                        try:
                            # "HH:MM" 形式を解析
                            hour, minute = map(int, arrival_time_str.split(':'))
                            scheduled_arrival = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            
                            # 日付をまたぐ場合の処理
                            if scheduled_arrival < scheduled_departure:
                                scheduled_arrival = scheduled_arrival + timedelta(days=1)
                        except Exception as e:
                            logger.warning(f"到着時刻の解析に失敗しました: {arrival_time_str}, エラー: {str(e)}")
                            scheduled_arrival = scheduled_departure + timedelta(minutes=20)  # フォールバック
                    else:
                        scheduled_arrival = scheduled_departure + timedelta(minutes=20)  # 時刻不明の場合のダミーデータ
                    
                    # 予測到着時刻を推定 (実際のデータがない場合は簡易計算)
                    arrival_delay = (predicted_departure - scheduled_departure).total_seconds() if predicted_departure and scheduled_departure else 0
                    predicted_arrival = scheduled_arrival + timedelta(seconds=arrival_delay) if scheduled_arrival else None
                    
                    # 新しいBusInfoオブジェクトを作成
                    bus_info = BusInfo(
                        destination=destination,
                        bus_number=bus_number,
                        stop_number=stop_number,
                        scheduled_departure_time=scheduled_departure,
                        predicted_departure_time=predicted_departure,
                        scheduled_arrival_time=scheduled_arrival,
                        predicted_arrival_time=predicted_arrival,
                        estimated_departure_minutes=estimated_minutes,
                        is_next_bus=(i == 0),  # 最初のバスが次のバス
                        is_active=True
                    )
                    
                    # データベースに保存
                    db.session.add(bus_info)
                    logger.info(f"バス情報を追加しました: {destination} - {bus_number} (残り{estimated_minutes}分)")
                
                except Exception as e:
                    logger.error(f"{destination}のバスエントリー処理エラー: {str(e)}")
            
            # すべての変更をコミット
            db.session.commit()
            logger.info(f"{destination}のバス情報をデータベースに保存しました")
            
            return True
            
        except Exception as e:
            logger.error(f"HTML処理中のエラー: {str(e)}")
            return False


# サービスのインスタンスを作成
bus_data_service = BusDataService()