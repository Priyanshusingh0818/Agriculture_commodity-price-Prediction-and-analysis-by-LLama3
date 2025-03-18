# AgriTech Market Advisor

A market insights and price prediction advisory system for farmers powered by LLaMA 3 and Groq.

## Features

- Historical price analysis with trend detection
- Market sentiment analysis from news reports
- Weather impact predictions
- Personalized selling advice using LLaMA 3 via Groq
- Easy-to-use web interface built with Streamlit
- Command-line interface for scripting and automation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/agritech-advisor.git
cd agritech-advisor
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up your Groq API key:
   - Create an account at https://console.groq.com/
   - Get your API key from the console
   - Edit `config.py` and add your API key

## Usage

### Web Interface

Run the Streamlit web app:

```bash
streamlit run app.py
```

This will open a browser window with the interactive dashboard.

### Command Line Interface

For scripting or automated tasks, use the CLI:

```bash
python cli.py --crop wheat --timeframe "1 month" --query "Should I sell my wheat now or wait?" --output advice.json
```

Options:
- `--crop`: The crop to analyze (default: wheat)
- `--timeframe`: Analysis timeframe (default: 1 month)
- `--query`: The farmer's question or query
- `--refresh`: Force refresh all data
- `--output`: Save results to a JSON file

## Configuration

Edit `config.py` to customize:
- API keys
- LLaMA 3 model selection
- Supported crops and timeframes
- Data source paths

## How It Works

1. **Data Collection**: The system fetches or generates historical price data, market news, and weather forecasts.
2. **Data Analysis**: It analyzes price trends, market sentiment, and potential weather impacts.
3. **LLM Processing**: The LLaMA 3 model processes the analyzed data and farmer query to generate personalized advice.
4. **Presentation**: Results are displayed in an easy-to-understand format, with clear recommendations.

## Extending the System

To add support for new crops:
1. Add the crop to `DEFAULT_CROPS` in `config.py`
2. Update weather impact analysis in `data_analyzer.py` if needed
3. Restart the application

To add new data sources:
1. Create a new method in `data_collector.py`
2. Update the analysis in `data_analyzer.py`
3. Modify the LLM prompt in `llm_interface.py` to include the new data

## Requirements

- Python 3.8+
- Groq API key
- Dependencies listed in requirements.txt

## License

MIT License