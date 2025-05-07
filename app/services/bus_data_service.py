import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from flask import current_app
from app.models.bus_info import BusInfo
from app import db

logger = logging.getLogger(__name__)

class BusDataService:
    """Service for fetching bus data"""
    
    def __init__(self):
        self.source = "野崎"
        self.destinations = {
            "三鷹駅": {"url_suffix": "to-be-determined"},
            "吉祥寺駅": {"url_suffix": "to-be-determined"},
            "武蔵境駅南口": {"url_suffix": "to-be-determined"},
            "調布駅北口": {"url_suffix": "to-be-determined"}
        }
        self.base_url = "https://transfer.odakyubus.co.jp/blsys/navi"  # Will need to be updated with actual URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.retry_count = 3
    
    def fetch_all_bus_data(self):
        """
        Fetch bus data for all destinations
        """
        logger.info("Starting bus data fetch for all destinations")
        
        # First, deactivate all current data
        BusInfo.deactivate_all()
        
        success_count = 0
        
        # Fetch data for each destination
        for destination, config in self.destinations.items():
            try:
                logger.info(f"Fetching data for destination: {destination}")
                self._fetch_destination_data(destination, config)
                success_count += 1
            except Exception as e:
                logger.error(f"Error fetching data for {destination}: {str(e)}")
        
        logger.info(f"Bus data fetch completed. Successfully updated {success_count}/{len(self.destinations)} destinations")
        
        return success_count == len(self.destinations)
    
    def _fetch_destination_data(self, destination, config):
        """
        Fetch bus data for a specific destination
        """
        # In a real implementation, we would:
        # 1. First check if there's an official API available
        # 2. If not, fall back to web scraping
        
        # For now, we'll implement the scraping approach
        url = f"{self.base_url}/{config['url_suffix']}"
        
        # Try to fetch the data, with retries
        for attempt in range(self.retry_count):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # Parse and process the data
                self._process_html_response(destination, response.text)
                return True
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt+1}/{self.retry_count} failed for {destination}: {str(e)}")
                if attempt == self.retry_count - 1:
                    raise
        
        return False
    
    def _process_html_response(self, destination, html_content):
        """
        Process HTML content from the bus information website
        
        Note: This is a placeholder implementation. The actual selectors and parsing
        logic will need to be updated based on the real website structure.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Find bus entries (the actual selectors will need to be determined)
        bus_entries = soup.select('.bus-entry')  # Example selector
        
        if not bus_entries:
            logger.warning(f"No bus entries found for {destination}")
            return False
        
        # Process each bus entry
        for i, entry in enumerate(bus_entries):
            try:
                # Extract data (these are placeholder selectors)
                bus_number = entry.select_one('.bus-number').text.strip()
                stop_number = entry.select_one('.stop-number').text.strip()
                
                # Extract time information - these are placeholder implementations
                scheduled_departure_str = entry.select_one('.scheduled-departure').text.strip()
                predicted_departure_str = entry.select_one('.predicted-departure').text.strip()
                
                # Extract minutes remaining text
                minutes_text = entry.select_one('.remaining-time').text.strip()
                minutes_match = re.search(r'約(\d+)分で発車します', minutes_text)
                estimated_minutes = int(minutes_match.group(1)) if minutes_match else None
                
                # Parse the times (dummy implementation)
                now = datetime.now()
                scheduled_departure = now + timedelta(minutes=30)  # Dummy data
                predicted_departure = now + timedelta(minutes=estimated_minutes) if estimated_minutes else scheduled_departure
                
                # Create a new BusInfo object
                bus_info = BusInfo(
                    destination=destination,
                    bus_number=bus_number,
                    stop_number=stop_number,
                    scheduled_departure_time=scheduled_departure,
                    predicted_departure_time=predicted_departure,
                    scheduled_arrival_time=scheduled_departure + timedelta(minutes=20),  # Dummy data
                    predicted_arrival_time=predicted_departure + timedelta(minutes=20),  # Dummy data
                    estimated_departure_minutes=estimated_minutes,
                    is_next_bus=(i == 0),  # The first bus is the next one
                    is_active=True
                )
                
                # Save to the database
                db.session.add(bus_info)
            
            except Exception as e:
                logger.error(f"Error processing bus entry for {destination}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        return True


# Create an instance of the service
bus_data_service = BusDataService()