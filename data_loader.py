"""
Data Loader Module for Market Haze

This module is responsible for fetching historical data from external APIs.
It provides functions to retrieve:
- Mumbai Air Quality Index (AQI) data from Open-Meteo API
- Nifty 50 stock market index data from Yahoo Finance via yfinance

The module handles API errors gracefully and returns data in pandas DataFrame format
with datetime indices for easy alignment and analysis.
"""

import pandas as pd
from datetime import datetime, timedelta


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


def fetch_mumbai_aqi(days: int = 365) -> pd.DataFrame:
    """
    Fetch Mumbai AQI data for the specified number of days.
    
    Args:
        days: Number of days of historical data to fetch (default: 365)
    
    Returns:
        DataFrame with columns: ['date', 'aqi']
        
    Raises:
        APIError: If the Open-Meteo API request fails
    """
    try:
        import openmeteo_requests
        import requests_cache
        from retry_requests import retry
        
        # Setup the Open-Meteo API client with cache and retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # Mumbai coordinates
        latitude = 19.0760
        longitude = 72.8777
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # API parameters
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": "pm10"  # Using PM10 as a proxy for AQI
        }
        
        # Make API request
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        # Process hourly data
        hourly = response.Hourly()
        hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
        
        # Create date range
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        hourly_data["pm10"] = hourly_pm10
        
        # Create DataFrame from hourly data
        df = pd.DataFrame(data=hourly_data)
        
        # Convert PM10 to a simple AQI scale (simplified calculation)
        # Note: This is a simplified AQI calculation using PM10 as a proxy
        # In production, you would use the official AQI calculation formula
        df['aqi'] = df['pm10']
        
        # Resample to daily values (take daily mean)
        # This converts hourly data to daily data by averaging
        df = df.set_index('date')
        df = df.resample('D').mean()
        
        # Drop the pm10 column, keep only aqi, and remove any NaN values
        df = df[['aqi']].dropna()
        
        # Convert timezone-aware index to timezone-naive for compatibility
        # This ensures alignment with Nifty 50 data works correctly
        df.index = df.index.tz_localize(None)
        
        return df
        
    except Exception as e:
        raise APIError(f"Data Loader: API Error - Failed to fetch AQI data from Open-Meteo: {str(e)}")


def fetch_nifty50(days: int = 365) -> pd.DataFrame:
    """
    Fetch Nifty 50 index data for the specified number of days.
    
    Args:
        days: Number of days of historical data to fetch (default: 365)
    
    Returns:
        DataFrame with columns: ['date', 'close']
        
    Raises:
        APIError: If the yfinance request fails
    """
    try:
        import yfinance as yf
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch Nifty 50 data using ticker symbol ^NSEI
        # ^NSEI is the Yahoo Finance ticker for the Nifty 50 index
        ticker = yf.Ticker("^NSEI")
        df = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        # Validate that we received data
        if df.empty:
            raise APIError("Data Loader: API Error - No data returned from yfinance for Nifty 50")
        
        # Keep only the closing price column and standardize naming
        # We use closing prices as they represent the final market value for each day
        df = df[['Close']].copy()
        df.columns = ['close']
        df.index.name = 'date'
        
        # Ensure timezone-naive index for compatibility with AQI data
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        # Normalize to date only (remove time component if present)
        df.index = pd.to_datetime(df.index.date)
        
        return df
        
    except Exception as e:
        if isinstance(e, APIError):
            raise
        raise APIError(f"Data Loader: API Error - Failed to fetch Nifty 50 data from yfinance: {str(e)}")
