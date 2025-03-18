#!/usr/bin/env python3
# cli.py

import argparse
import json
import os
import sys
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cli.log"),
        logging.StreamHandler()
    ]
)

def main():
    # Make sure the modules are in the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import our modules
    import config as config_module
    from data_collector import DataCollector
    from data_analyzer import DataAnalyzer
    from llm_interface import LLMAdvisor
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AgriTech Market Advisor CLI')
    parser.add_argument('--crop', type=str, default='wheat', help='Crop to analyze')
    parser.add_argument('--timeframe', type=str, default='1 month', help='Analysis timeframe')
    parser.add_argument('--query', type=str, required=True, help='Farmer query')
    parser.add_argument('--refresh', action='store_true', help='Force refresh all data')
    parser.add_argument('--output', type=str, help='Output file path for JSON results')
    
    args = parser.parse_args()
    
    print(f"🌾 AgriTech Market Advisor CLI")
    print(f"Analyzing {args.crop} for {args.timeframe} timeframe")
    
    # Initialize components
    collector = DataCollector(config_module)
    analyzer = DataAnalyzer(collector)
    advisor = LLMAdvisor(config_module)
    
    # Refresh data if requested
    if args.refresh:
        print("Refreshing data...")
        collector.load_or_fetch_historical_prices(args.crop, force_refresh=True)
        collector.load_or_fetch_market_news(args.crop, force_refresh=True)
        collector.load_or_fetch_weather_forecast(force_refresh=True)
    
    # Get comprehensive analysis
    print("Analyzing market data...")
    analysis = analyzer.get_comprehensive_analysis(args.crop, args.timeframe)
    
    # Get LLM-generated advice
    print("Generating personalized advice...")
    advisory = advisor.get_advisory(analysis, args.query, force_refresh=args.refresh)
    
    # Display results
    print("\n===== MARKET ADVICE =====")
    print(advisory['advice'])
    
    print("\n===== DATA SUMMARY =====")
    for key, value in advisory['data_summary'].items():
        print(f"- {key.replace('_', ' ').title()}: {value}")
    
    print(f"\nGenerated on: {advisory['timestamp']}")
    
    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(advisory, f, indent=2)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()