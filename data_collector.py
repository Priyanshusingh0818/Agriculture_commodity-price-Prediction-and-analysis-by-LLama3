# data_collector.py

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.historical_data = None
        self.news_data = None
        self.weather_data = None
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
    
    def load_or_fetch_historical_prices(self, crop, force_refresh=False):
        """Load historical price data from file or fetch from API if needed"""
        file_path = self.config.HISTORICAL_PRICE_DATA_PATH
        
        if not force_refresh and os.path.exists(file_path):
            logging.info(f"Loading historical price data for {crop} from file")
            self.historical_data = pd.read_csv(file_path)
            return self.historical_data
        
        # In a real application, you would fetch data from an agricultural API
        # For this example, we'll create sample data
        logging.info(f"Generating sample historical price data for {crop}")
        
        # Generate sample data for the last 2 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*2)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create synthetic price data with some trends and seasonality
        import numpy as np
        base_price = 500 if crop == "wheat" else 400 if crop == "corn" else 600
        trend = np.linspace(0, 100, len(date_range))
        seasonality = 50 * np.sin(np.linspace(0, 4*np.pi, len(date_range)))
        noise = np.random.normal(0, 20, len(date_range))
        
        prices = base_price + trend + seasonality + noise
        
        self.historical_data = pd.DataFrame({
            'date': date_range,
            'crop': crop,
            'price': prices
        })
        
        # Save to CSV
        self.historical_data.to_csv(file_path, index=False)
        logging.info(f"Saved historical price data to {file_path}")
        
        return self.historical_data
    
    def load_or_fetch_market_news(self, crop, days=30, force_refresh=False):
        """Load market news data from file or fetch from API if needed"""
        file_path = self.config.MARKET_NEWS_DATA_PATH
        
        if not force_refresh and os.path.exists(file_path):
            logging.info(f"Loading market news data for {crop} from file")
            self.news_data = pd.read_csv(file_path)
            return self.news_data
        
        # In a real application, you would fetch news from an agricultural news API
        # For this example, we'll create sample data
        logging.info(f"Generating sample market news data for {crop}")
        
        # Sample news headlines and sentiment
        news_samples = [
            {"headline": f"Global demand for {crop} increases amid supply concerns", "sentiment": "positive"},
            {"headline": f"New trade deal may boost {crop} exports", "sentiment": "positive"},
            {"headline": f"Weather conditions threaten {crop} yield in major producing regions", "sentiment": "negative"},
            {"headline": f"{crop.capitalize()} prices stabilize after recent volatility", "sentiment": "neutral"},
            {"headline": f"Report shows increased {crop} stockpiles", "sentiment": "negative"},
            {"headline": f"Analysts predict strong {crop} market for next quarter", "sentiment": "positive"}
        ]
        
        # Generate dates for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create news entries
        import random
        news_entries = []
        for date in date_range:
            # Randomly choose 0-2 news items for each day
            daily_news_count = random.randint(0, 2)
            for _ in range(daily_news_count):
                news_entry = random.choice(news_samples)
                news_entries.append({
                    'date': date,
                    'crop': crop,
                    'headline': news_entry["headline"],
                    'sentiment': news_entry["sentiment"]
                })
        
        self.news_data = pd.DataFrame(news_entries)
        
        # Save to CSV
        self.news_data.to_csv(file_path, index=False)
        logging.info(f"Saved market news data to {file_path}")
        
        return self.news_data
    
    def load_or_fetch_weather_forecast(self, region="midwest", force_refresh=False):
        """Load weather forecast data from file or fetch from API if needed"""
        file_path = self.config.WEATHER_DATA_PATH
        
        if not force_refresh and os.path.exists(file_path):
            logging.info(f"Loading weather forecast data for {region} from file")
            self.weather_data = pd.read_csv(file_path)
            return self.weather_data
        
        # In a real application, you would fetch weather data from a weather API
        # For this example, we'll create sample data
        logging.info(f"Generating sample weather forecast data for {region}")
        
        # Generate dates for the next 14 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=14)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create weather entries
        import random
        weather_entries = []
        for date in date_range:
            weather_entries.append({
                'date': date,
                'region': region,
                'temperature': random.uniform(15, 30),  # Temperature in Celsius
                'precipitation': random.uniform(0, 20),  # Precipitation in mm
                'conditions': random.choice(['sunny', 'cloudy', 'rainy', 'partly cloudy'])
            })
        
        self.weather_data = pd.DataFrame(weather_entries)
        
        # Save to CSV
        self.weather_data.to_csv(file_path, index=False)
        logging.info(f"Saved weather forecast data to {file_path}")
        
        return self.weather_data