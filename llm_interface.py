# llm_interface.py

import json
import logging
import groq
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMAdvisor:
    def __init__(self, config):
        self.config = config
        self.client = groq.Client(api_key=config.GROQ_API_KEY)
        self.model = config.MODEL_NAME
        self.response_cache = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs('cache', exist_ok=True)
    
    def get_advisory(self, analysis_data, farmer_query, force_refresh=False):
        """Generate market advisory"""
        # Create a cache key based on data and query
        import hashlib
        cache_key = hashlib.md5(f"{str(analysis_data)}_{farmer_query}".encode()).hexdigest()
        cache_file = f"cache/{cache_key}.json"
        
        # Check cache unless force_refresh is True
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_response = json.load(f)
                logging.info(f"Using cached LLM response for query: {farmer_query[:30]}...")
                return cached_response
            except Exception as e:
                logging.error(f"Error reading cache: {e}")
        
        logging.info(f"Generating new LLM advisory for query: {farmer_query[:30]}...")
        
        # Prepare context and prompt for the LLM
        crop = analysis_data['crop']
        timeframe = analysis_data['timeframe']
        price_analysis = analysis_data['price_analysis']
        sentiment_analysis = analysis_data['sentiment_analysis']
        weather_analysis = analysis_data['weather_analysis']
        
        # Format the data for the prompt
        prompt = self._format_prompt(crop, timeframe, price_analysis, sentiment_analysis, weather_analysis, farmer_query)
        
        try:
            # Call Groq API with LLaMA 3 model
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an agricultural market analyst and advisor. "
                     "You provide farmers with informed, practical advice on crop marketing decisions "
                     "based on data analysis, market trends, and weather forecasts. Your advice should "
                     "be clear, concise, and actionable with specific recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent, factual responses
                max_tokens=1024
            )
            
            # Extract the response text
            advice_text = response.choices[0].message.content
            
            # Structure the response
            advisory_response = {
                "query": farmer_query,
                "crop": crop,
                "advice": advice_text,
                "data_summary": {
                    "current_price": price_analysis.get('current_price'),
                    "price_trend": price_analysis.get('trend'),
                    "projected_price_change": price_analysis.get('projection_pct'),
                    "market_sentiment": sentiment_analysis.get('sentiment_trend'),
                    "weather_impact": weather_analysis.get('weather_impact')
                },
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Cache the response
            with open(cache_file, 'w') as f:
                json.dump(advisory_response, f)
            
            logging.info(f"Advisory generated and cached")
            return advisory_response
            
        except Exception as e:
            logging.error(f"Error generating advisory: {e}")
            return {
                "query": farmer_query,
                "crop": crop,
                "advice": f"Unable to generate advisory at this time. Error: {str(e)}",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _format_prompt(self, crop, timeframe, price_analysis, sentiment_analysis, weather_analysis, farmer_query):
        """Format the data into a prompt for the LLM"""
        
        # Create a detailed context from the analysis data
        context = f"""
Here is the current market analysis for {crop.upper()}:

PRICE ANALYSIS ({timeframe}):
- Current price: ${price_analysis.get('current_price', 'N/A'):.2f} per bushel
- Price trend: {price_analysis.get('trend', 'N/A')}
- Price change: {price_analysis.get('price_change_pct', 'N/A'):.2f}% over the last {timeframe}
- Projected price change: {price_analysis.get('projection_pct', 'N/A'):.2f}% in the coming {timeframe}
- Price volatility: {price_analysis.get('volatility', 'N/A'):.2f}

MARKET SENTIMENT:
- Overall sentiment: {sentiment_analysis.get('sentiment_trend', 'N/A')}
- Recent headlines:
{chr(10).join(['  - ' + headline for headline in sentiment_analysis.get('headlines', [])[:3]])}

WEATHER FORECAST IMPACT:
- Weather impact: {weather_analysis.get('weather_impact', 'N/A')}
- Explanation: {weather_analysis.get('explanation', 'N/A')}
- Average temperature: {weather_analysis.get('average_temperature', 'N/A'):.1f}°C
- Total precipitation forecast: {weather_analysis.get('total_precipitation', 'N/A'):.1f} mm

Based on this analysis, provide specific advice in response to the farmer's question:
"{farmer_query}"

Your advice should include:
1. A clear recommendation (sell now, hold, or partial sale)
2. Reasoning behind your recommendation
3. Timing suggestions (when to sell if not now)
4. Risks to be aware of
5. Alternative strategies to consider
"""
        return context