# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging

# Import our modules
from config import *
from data_collector import DataCollector
from data_analyzer import DataAnalyzer
from llm_interface import LLMAdvisor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Initialize components
@st.cache_resource
def initialize_components():
    collector = DataCollector(config_module)
    analyzer = DataAnalyzer(collector)
    advisor = LLMAdvisor(config_module)
    return collector, analyzer, advisor

def main():
    st.set_page_config(page_title="AgriTech Market Advisor", page_icon="🌾", layout="wide")
    
    st.title("🌾 Market Advisor")
    
    # Initialize our components
    collector, analyzer, advisor = initialize_components()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        crop = st.selectbox("Select Crop", DEFAULT_CROPS)
        timeframe = st.selectbox("Analysis Timeframe", PREDICTION_TIMEFRAMES)
        
        st.header("Actions")
        refresh_data = st.button("Refresh Market Data")
        
        st.header("About")
        st.markdown("""
        This application uses LLaMA 3 via Groq to analyze 
        agricultural market data and provide personalized 
        advice to farmers about when to sell their crops.
        """)
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"{crop.capitalize()} Market Analysis")
        
        # Run analysis
        if refresh_data:
            with st.spinner("Refreshing data..."):
                # Force refresh all data
                collector.load_or_fetch_historical_prices(crop, force_refresh=True)
                collector.load_or_fetch_market_news(crop, force_refresh=True)
                collector.load_or_fetch_weather_forecast(force_refresh=True)
                st.success("Data refreshed successfully!")
        
        # Get comprehensive analysis
        with st.spinner("Analyzing market data..."):
            analysis = analyzer.get_comprehensive_analysis(crop, timeframe)
        
        # Display price chart if available
        chart_path = f"analysis/{crop}_{timeframe.replace(' ', '_')}_chart.png"
        if os.path.exists(chart_path):
            st.image(chart_path)
        
        # Display analysis results
        price_analysis = analysis['price_analysis']
        sentiment_analysis = analysis['sentiment_analysis']
        weather_analysis = analysis['weather_analysis']
        
        # Show price analysis
        st.subheader("Price Analysis")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Current Price", f"${price_analysis.get('current_price', 0):.2f}")
        with metrics_col2:
            st.metric("Price Trend", price_analysis.get('trend', 'Unknown'))
        with metrics_col3:
            st.metric("Projected Change", f"{price_analysis.get('projection_pct', 0):.2f}%")
        
        # Show sentiment analysis
        st.subheader("Market Sentiment")
        sentiment_col1, sentiment_col2 = st.columns(2)
        with sentiment_col1:
            st.metric("Sentiment", sentiment_analysis.get('sentiment_trend', 'Unknown'))
        with sentiment_col2:
            st.write(f"Based on {sentiment_analysis.get('positive_news_count', 0) + sentiment_analysis.get('negative_news_count', 0) + sentiment_analysis.get('neutral_news_count', 0)} news items")
        
        # Show recent headlines
        if sentiment_analysis.get('headlines'):
            st.write("Recent Headlines:")
            for headline in sentiment_analysis.get('headlines', [])[:5]:
                st.write(f"- {headline}")
        
        # Show weather analysis
        st.subheader("Weather Impact")
        st.write(f"Impact: {weather_analysis.get('weather_impact', 'Unknown')}")
        st.write(f"Explanation: {weather_analysis.get('explanation', 'No explanation available')}")
    
    with col2:
        st.header("Ask for Advice")
        farmer_query = st.text_area("Your Question:", 
                               value=f"Should I sell my {crop} now or wait?", 
                               height=100)
        
        get_advice = st.button("Get Advice")
        
        if get_advice:
            with st.spinner("Generating personalized advice..."):
                # Get LLM-generated advice
                advisory = advisor.get_advisory(analysis, farmer_query)
                
                # Display advice
                st.subheader("Market Advice")
                st.write(advisory['advice'])
                
                # Show data summary
               # Show data summary
                st.subheader("Data Summary")
                for key, value in advisory['data_summary'].items():
                    st.write(f"- {key.replace('_', ' ').title()}: {value}")
                
                # Show timestamp
                st.caption(f"Generated on: {advisory['timestamp']}")
        
        # Show example questions
        st.subheader("Example Questions")
        examples = [
            f"Should I sell my {crop} now or wait a month?",
            f"What's the best time to sell {crop} in the next {timeframe}?",
            f"Is it better to sell half my {crop} now and wait for the rest?",
            f"How will the weather affect {crop} prices soon?",
            f"What risks should I consider before selling my {crop}?"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.farmer_query = example
                st.experimental_rerun()

if __name__ == "__main__":
    import sys
    
    # Make sure the modules are in the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import config as a module
    import config as config_module
    
    main()