# Market Haze

A Streamlit dashboard application that investigates and visualizes the correlation between Mumbai's Air Quality Index (AQI) and the Nifty 50 stock market index over the past year.

## Overview

Market Haze retrieves historical data from external APIs, processes it, and presents interactive visualizations to help users understand potential relationships between air quality and market performance.

## Features

- **Historical AQI Data**: Fetches Mumbai's Air Quality Index data for the past year from Open-Meteo API
- **Nifty 50 Index Data**: Retrieves India's benchmark stock market index data using yfinance
- **Correlation Analysis**: Computes and displays the Pearson correlation coefficient between AQI and market performance
- **Interactive Visualizations**: Plotly-powered charts with zoom, pan, and hover capabilities
- **Real-time Data Processing**: Handles missing values, aligns datasets, and performs statistical analysis

## Data Sources

- **AQI Data**: [Open-Meteo API](https://open-meteo.com/) - Air quality data for Mumbai (19.0760° N, 72.8777° E)
- **Nifty 50 Data**: [Yahoo Finance](https://finance.yahoo.com/) via yfinance library - Ticker symbol `^NSEI`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd market-haze
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

## Project Structure

```
market-haze/
├── app.py                      # Main Streamlit dashboard application
├── data_loader.py              # API data fetching functions
├── data_processor.py           # Data cleaning and analysis functions
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
└── tests/                      # Test suite
    ├── conftest.py             # Shared test fixtures
    ├── property_tests/         # Property-based tests
    └── test_*.py               # Unit tests
```

## Dependencies

- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance data fetcher
- **openmeteo-requests**: Open-Meteo API client
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library
- **hypothesis**: Property-based testing framework
- **pytest**: Testing framework

## Testing

Run the test suite:
```bash
pytest
```

Run property-based tests:
```bash
pytest tests/property_tests/
```

## Development

The application follows a three-layer architecture:

1. **Data Layer** (`data_loader.py`): Fetches raw data from external APIs
2. **Processing Layer** (`data_processor.py`): Handles data cleaning, alignment, and statistical computations
3. **Presentation Layer** (`app.py`): Streamlit UI that orchestrates data flow and renders visualizations

### API Documentation

#### Data Loader Functions

**`fetch_mumbai_aqi(days: int = 365) -> pd.DataFrame`**
- Fetches Mumbai AQI data from Open-Meteo API
- Parameters:
  - `days`: Number of days of historical data (default: 365)
- Returns: DataFrame with datetime index and 'aqi' column
- Raises: `APIError` if the API request fails

**`fetch_nifty50(days: int = 365) -> pd.DataFrame`**
- Fetches Nifty 50 index data from Yahoo Finance
- Parameters:
  - `days`: Number of days of historical data (default: 365)
- Returns: DataFrame with datetime index and 'close' column
- Raises: `APIError` if the API request fails

#### Data Processor Functions

**`handle_missing_values(df: pd.DataFrame, method: str = 'forward_fill') -> pd.DataFrame`**
- Handles missing values in datasets
- Parameters:
  - `df`: DataFrame with potential missing values
  - `method`: Strategy to use ('forward_fill', 'drop', 'interpolate')
- Returns: DataFrame with missing values handled

**`align_datasets(aqi_df: pd.DataFrame, nifty_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]`**
- Aligns two datasets to common dates
- Parameters:
  - `aqi_df`: DataFrame with AQI data
  - `nifty_df`: DataFrame with Nifty 50 data
- Returns: Tuple of aligned DataFrames with matching indices

**`compute_correlation(aqi_values: pd.Series, nifty_values: pd.Series) -> float`**
- Computes Pearson correlation coefficient
- Parameters:
  - `aqi_values`: Series of AQI values
  - `nifty_values`: Series of Nifty 50 values
- Returns: Correlation coefficient between -1 and 1

#### Visualization Functions

**`create_time_series_chart(...) -> go.Figure`**
- Creates interactive Plotly line chart for time series data
- Returns: Plotly Figure object with zoom, pan, and hover features

**`create_scatter_plot(...) -> go.Figure`**
- Creates interactive scatter plot with optional trend line
- Returns: Plotly Figure object for correlation visualization

### Troubleshooting

**API Connection Issues**
- If you encounter API errors, check your internet connection
- The Open-Meteo API has rate limits; wait a few minutes if you hit them
- Yahoo Finance data may be delayed or unavailable during market hours

**Missing Data**
- AQI data is available daily, but may have gaps
- Nifty 50 data is only available on trading days (excludes weekends/holidays)
- The application handles missing values automatically using forward fill

**Performance**
- First run may be slower due to API requests
- Subsequent runs use cached data (cache expires after 1 hour)
- Large date ranges (>365 days) may take longer to process

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests.

### Development Setup

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Run property-based tests:
```bash
pytest tests/property_tests/ -v
```

## Acknowledgments

- **Open-Meteo**: For providing free air quality data API
- **Yahoo Finance**: For providing financial market data
- **Streamlit**: For the excellent web application framework
