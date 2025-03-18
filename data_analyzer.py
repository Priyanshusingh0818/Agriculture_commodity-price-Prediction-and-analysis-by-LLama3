# data_analyzer.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataAnalyzer:
    def __init__(self, data_collector):
        self.data_collector = data_collector
        self.analysis_results = {}
        
        # Create analysis directory if it doesn't exist
        os.makedirs('analysis', exist_ok=True)
    
    def analyze_price_trends(self, crop, timeframe="1 month"):
        """Analyze price trends for a specific crop over a timeframe"""
        logging.info(f"Analyzing price trends for {crop} over {timeframe}")
        
        # Get historical price data
        historical_data = self.data_collector.load_or_fetch_historical_prices(crop)
        
        # Convert timeframe to days
        if timeframe == "1 week":
            days = 7
        elif timeframe == "1 month":
            days = 30
        elif timeframe == "3 months":
            days = 90
        else:
            days = 30  # Default to 1 month
        
        # Filter data for the specified timeframe
        end_date = datetime.now()
        if isinstance(historical_data['date'][0], str):
            historical_data['date'] = pd.to_datetime(historical_data['date'])
        
        start_date = end_date - timedelta(days=days)
        filtered_data = historical_data[historical_data['date'] >= start_date]
        
        # Calculate key metrics
        if len(filtered_data) > 0:
            current_price = filtered_data['price'].iloc[-1]
            avg_price = filtered_data['price'].mean()
            price_change = filtered_data['price'].iloc[-1] - filtered_data['price'].iloc[0]
            price_change_pct = (price_change / filtered_data['price'].iloc[0]) * 100
            
            # Determine trend
            if price_change_pct > 5:
                trend = "strongly increasing"
            elif price_change_pct > 1:
                trend = "slightly increasing"
            elif price_change_pct < -5:
                trend = "strongly decreasing"
            elif price_change_pct < -1:
                trend = "slightly decreasing" 
            else:
                trend = "stable"
            
            # Calculate volatility
            volatility = filtered_data['price'].std()
            
            # Generate a price projection for the next period
            # This is a simplified model - in practice, you'd use more sophisticated forecasting
            if len(filtered_data) > 7:
                recent_trend = filtered_data['price'].iloc[-7:].mean() - filtered_data['price'].iloc[-14:-7].mean()
                projected_price = current_price + recent_trend
                projection_pct = (projected_price / current_price - 1) * 100
            else:
                recent_trend = 0
                projected_price = current_price
                projection_pct = 0
            
            analysis = {
                'crop': crop,
                'timeframe': timeframe,
                'current_price': current_price,
                'average_price': avg_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'trend': trend,
                'volatility': volatility,
                'projected_price': projected_price,
                'projection_pct': projection_pct
            }
            
            self.analysis_results[f"{crop}_{timeframe}"] = analysis
            
            # Generate a visualization
            self._generate_price_chart(filtered_data, crop, timeframe)
            
            return analysis
        else:
            logging.warning(f"No data available for {crop} over {timeframe}")
            return None
    
    def analyze_market_sentiment(self, crop):
        """Analyze market sentiment from news data"""
        logging.info(f"Analyzing market sentiment for {crop}")
        
        # Get news data
        news_data = self.data_collector.load_or_fetch_market_news(crop)
        
        if len(news_data) > 0:
            # Count sentiment
            sentiment_counts = news_data['sentiment'].value_counts()
            
            # Calculate sentiment score (-1 to 1)
            pos_count = sentiment_counts.get('positive', 0)
            neg_count = sentiment_counts.get('negative', 0)
            neutral_count = sentiment_counts.get('neutral', 0)
            
            total_count = pos_count + neg_count + neutral_count
            if total_count > 0:
                sentiment_score = (pos_count - neg_count) / total_count
            else:
                sentiment_score = 0
            
            # Determine sentiment trend
            if sentiment_score > 0.5:
                sentiment_trend = "strongly positive"
            elif sentiment_score > 0.1:
                sentiment_trend = "positive"
            elif sentiment_score < -0.5:
                sentiment_trend = "strongly negative"
            elif sentiment_score < -0.1:
                sentiment_trend = "negative"
            else:
                sentiment_trend = "neutral"
            
            analysis = {
                'crop': crop,
                'sentiment_score': sentiment_score,
                'sentiment_trend': sentiment_trend,
                'positive_news_count': pos_count,
                'negative_news_count': neg_count,
                'neutral_news_count': neutral_count,
                'headlines': news_data['headline'].tolist()
            }
            
            self.analysis_results[f"{crop}_sentiment"] = analysis
            return analysis
        else:
            logging.warning(f"No news data available for {crop}")
            return None
    
    def analyze_weather_impact(self, crop, region="midwest"):
        """Analyze potential weather impact on crop prices"""
        logging.info(f"Analyzing weather impact for {crop} in {region}")
        
        # Get weather data
        weather_data = self.data_collector.load_or_fetch_weather_forecast(region)
        
        if len(weather_data) > 0:
            # Calculate average temperature and precipitation
            avg_temp = weather_data['temperature'].mean()
            total_precip = weather_data['precipitation'].sum()
            
            # Simple weather impact analysis
            # This is a simplified model - in practice, you'd use more sophisticated analysis
            if crop == "wheat":
                # Wheat prefers moderate temperatures and moderate rainfall
                if avg_temp > 25 and total_precip < 10:
                    impact = "negative"
                    explanation = "High temperatures and low precipitation may stress wheat crops."
                elif avg_temp < 15 and total_precip > 30:
                    impact = "negative"
                    explanation = "Low temperatures and excessive rainfall may damage wheat crops."
                else:
                    impact = "neutral to positive"
                    explanation = "Weather conditions appear favorable for wheat crops."
            elif crop == "corn":
                # Corn prefers warm temperatures and moderate to high rainfall
                # Corn prefers warm temperatures and moderate to high rainfall
                if avg_temp < 18 or total_precip < 15:
                    impact = "negative"
                    explanation = "Low temperatures or insufficient rainfall may reduce corn yields."
                elif avg_temp > 30 and total_precip < 20:
                    impact = "negative"
                    explanation = "High heat and insufficient moisture may stress corn crops."
                else:
                    impact = "neutral to positive"
                    explanation = "Weather conditions appear favorable for corn growth."
            elif crop == "soybeans":
                # Soybeans prefer warm temperatures and moderate rainfall
                if avg_temp < 20 or total_precip < 10:
                    impact = "negative"
                    explanation = "Low temperatures or dry conditions may reduce soybean yields."
                elif total_precip > 40:
                    impact = "negative"
                    explanation = "Excessive rainfall may lead to disease pressure in soybeans."
                else:
                    impact = "neutral to positive"
                    explanation = "Weather conditions appear favorable for soybean development."
            else:
                # Default case for other crops
                impact = "uncertain"
                explanation = f"Weather impact analysis not specifically calibrated for {crop}."
            
            analysis = {
                'crop': crop,
                'region': region,
                'average_temperature': avg_temp,
                'total_precipitation': total_precip,
                'weather_impact': impact,
                'explanation': explanation
            }
            
            self.analysis_results[f"{crop}_weather"] = analysis
            return analysis
        else:
            logging.warning(f"No weather data available for {region}")
            return None
    
    def _generate_price_chart(self, price_data, crop, timeframe):
        """Generate and save a price chart"""
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(price_data['date'], price_data['price'])
            plt.title(f"{crop.capitalize()} Price Trend - {timeframe}")
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.grid(True)
            plt.tight_layout()
            
            # Save the chart
            chart_path = f"analysis/{crop}_{timeframe.replace(' ', '_')}_chart.png"
            plt.savefig(chart_path)
            plt.close()
            logging.info(f"Chart saved to {chart_path}")
            
            return chart_path
        except Exception as e:
            logging.error(f"Error generating chart: {e}")
            return None
    
    def get_comprehensive_analysis(self, crop, timeframe="1 month"):
        """Get comprehensive analysis for a crop by combining multiple analyses"""
        logging.info(f"Generating comprehensive analysis for {crop}")
        
        # Run individual analyses if they haven't been run yet
        if f"{crop}_{timeframe}" not in self.analysis_results:
            self.analyze_price_trends(crop, timeframe)
        
        if f"{crop}_sentiment" not in self.analysis_results:
            self.analyze_market_sentiment(crop)
        
        if f"{crop}_weather" not in self.analysis_results:
            self.analyze_weather_impact(crop)
        
        # Combine results
        price_analysis = self.analysis_results.get(f"{crop}_{timeframe}", {})
        sentiment_analysis = self.analysis_results.get(f"{crop}_sentiment", {})
        weather_analysis = self.analysis_results.get(f"{crop}_weather", {})
        
        # Create comprehensive analysis
        comprehensive = {
            'crop': crop,
            'timeframe': timeframe,
            'price_analysis': price_analysis,
            'sentiment_analysis': sentiment_analysis,
            'weather_analysis': weather_analysis,
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        return comprehensive