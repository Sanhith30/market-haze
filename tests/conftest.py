"""
Shared test fixtures and configuration for Market Haze tests.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import strategies as st

# Add the project root to the Python path so tests can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Hypothesis Strategies for Generating Test DataFrames
# ============================================================================

@st.composite
def datetime_index_strategy(draw, min_size=1, max_size=100):
    """
    Generate a DatetimeIndex with random dates.
    
    Args:
        draw: Hypothesis draw function
        min_size: Minimum number of dates
        max_size: Maximum number of dates
    
    Returns:
        DatetimeIndex with sorted dates
    """
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Generate random dates
    dates = []
    for _ in range(size):
        days_offset = draw(st.integers(min_value=0, max_value=(end_date - start_date).days))
        date = start_date + timedelta(days=days_offset)
        dates.append(date)
    
    # Sort and remove duplicates
    dates = sorted(set(dates))
    return pd.DatetimeIndex(dates)


@st.composite
def aqi_dataframe_strategy(draw, min_size=1, max_size=100, allow_missing=False):
    """
    Generate a DataFrame with AQI data structure.
    
    Args:
        draw: Hypothesis draw function
        min_size: Minimum number of rows
        max_size: Maximum number of rows
        allow_missing: Whether to allow NaN values
    
    Returns:
        DataFrame with 'aqi' column and datetime index
    """
    date_index = draw(datetime_index_strategy(min_size=min_size, max_size=max_size))
    size = len(date_index)
    
    # Generate AQI values (typically 0-500 range)
    aqi_values = []
    for _ in range(size):
        if allow_missing and draw(st.booleans()):
            aqi_values.append(np.nan)
        else:
            aqi_values.append(draw(st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False)))
    
    df = pd.DataFrame({'aqi': aqi_values}, index=date_index)
    df.index.name = 'date'
    return df


@st.composite
def nifty_dataframe_strategy(draw, min_size=1, max_size=100, allow_missing=False):
    """
    Generate a DataFrame with Nifty 50 data structure.
    
    Args:
        draw: Hypothesis draw function
        min_size: Minimum number of rows
        max_size: Maximum number of rows
        allow_missing: Whether to allow NaN values
    
    Returns:
        DataFrame with 'close' column and datetime index
    """
    date_index = draw(datetime_index_strategy(min_size=min_size, max_size=max_size))
    size = len(date_index)
    
    # Generate Nifty 50 closing values (typically 10000-25000 range)
    close_values = []
    for _ in range(size):
        if allow_missing and draw(st.booleans()):
            close_values.append(np.nan)
        else:
            close_values.append(draw(st.floats(min_value=10000, max_value=25000, allow_nan=False, allow_infinity=False)))
    
    df = pd.DataFrame({'close': close_values}, index=date_index)
    df.index.name = 'date'
    return df


@st.composite
def aligned_dataframes_strategy(draw, min_size=5, max_size=50):
    """
    Generate two DataFrames with overlapping date indices.
    
    Args:
        draw: Hypothesis draw function
        min_size: Minimum number of overlapping dates
        max_size: Maximum number of overlapping dates
    
    Returns:
        Tuple of (aqi_df, nifty_df) with some overlapping dates
    """
    # Generate a common date range
    common_dates = draw(datetime_index_strategy(min_size=min_size, max_size=max_size))
    
    # Generate additional dates for each DataFrame
    extra_aqi_size = draw(st.integers(min_value=0, max_value=20))
    extra_nifty_size = draw(st.integers(min_value=0, max_value=20))
    
    # Create extended date ranges
    all_dates_aqi = list(common_dates)
    all_dates_nifty = list(common_dates)
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for _ in range(extra_aqi_size):
        days_offset = draw(st.integers(min_value=0, max_value=(end_date - start_date).days))
        all_dates_aqi.append(start_date + timedelta(days=days_offset))
    
    for _ in range(extra_nifty_size):
        days_offset = draw(st.integers(min_value=0, max_value=(end_date - start_date).days))
        all_dates_nifty.append(start_date + timedelta(days=days_offset))
    
    # Sort and remove duplicates
    all_dates_aqi = pd.DatetimeIndex(sorted(set(all_dates_aqi)))
    all_dates_nifty = pd.DatetimeIndex(sorted(set(all_dates_nifty)))
    
    # Generate AQI values
    aqi_values = [draw(st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False)) 
                  for _ in range(len(all_dates_aqi))]
    
    # Generate Nifty values
    nifty_values = [draw(st.floats(min_value=10000, max_value=25000, allow_nan=False, allow_infinity=False)) 
                    for _ in range(len(all_dates_nifty))]
    
    aqi_df = pd.DataFrame({'aqi': aqi_values}, index=all_dates_aqi)
    aqi_df.index.name = 'date'
    
    nifty_df = pd.DataFrame({'close': nifty_values}, index=all_dates_nifty)
    nifty_df.index.name = 'date'
    
    return aqi_df, nifty_df


# ============================================================================
# Pytest Fixtures for Sample Data
# ============================================================================

@pytest.fixture
def sample_aqi_data():
    """
    Fixture providing sample AQI data for testing.
    
    Returns:
        DataFrame with 30 days of sample AQI data
    """
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    aqi_values = [
        50, 75, 100, 85, 90, 110, 95, 80, 70, 65,
        55, 60, 75, 80, 95, 100, 105, 110, 115, 120,
        100, 90, 85, 80, 75, 70, 65, 60, 55, 50
    ]
    df = pd.DataFrame({'aqi': aqi_values}, index=dates)
    df.index.name = 'date'
    return df


@pytest.fixture
def sample_nifty_data():
    """
    Fixture providing sample Nifty 50 data for testing.
    
    Returns:
        DataFrame with 30 days of sample Nifty 50 data
    """
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    close_values = [
        21000, 21100, 21200, 21150, 21300, 21400, 21350, 21250, 21200, 21100,
        21050, 21000, 21100, 21200, 21300, 21400, 21500, 21600, 21700, 21800,
        21750, 21650, 21550, 21450, 21350, 21250, 21150, 21050, 20950, 20850
    ]
    df = pd.DataFrame({'close': close_values}, index=dates)
    df.index.name = 'date'
    return df


@pytest.fixture
def sample_aqi_with_missing():
    """
    Fixture providing sample AQI data with missing values.
    
    Returns:
        DataFrame with 20 days of AQI data including NaN values
    """
    dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
    aqi_values = [
        50, np.nan, 100, 85, np.nan, 110, 95, 80, np.nan, 65,
        55, 60, np.nan, 80, 95, np.nan, 105, 110, 115, np.nan
    ]
    df = pd.DataFrame({'aqi': aqi_values}, index=dates)
    df.index.name = 'date'
    return df


@pytest.fixture
def sample_nifty_with_missing():
    """
    Fixture providing sample Nifty 50 data with missing values.
    
    Returns:
        DataFrame with 20 days of Nifty 50 data including NaN values
    """
    dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
    close_values = [
        21000, np.nan, 21200, 21150, np.nan, 21400, 21350, 21250, np.nan, 21100,
        21050, 21000, np.nan, 21200, 21300, np.nan, 21500, 21600, 21700, np.nan
    ]
    df = pd.DataFrame({'close': close_values}, index=dates)
    df.index.name = 'date'
    return df


@pytest.fixture
def sample_misaligned_data():
    """
    Fixture providing two DataFrames with different date ranges.
    
    Returns:
        Tuple of (aqi_df, nifty_df) with partially overlapping dates
    """
    # AQI data: Jan 1 - Jan 25
    aqi_dates = pd.date_range(start='2024-01-01', periods=25, freq='D')
    aqi_values = list(range(50, 75))
    aqi_df = pd.DataFrame({'aqi': aqi_values}, index=aqi_dates)
    aqi_df.index.name = 'date'
    
    # Nifty data: Jan 10 - Feb 10 (overlaps Jan 10-25)
    nifty_dates = pd.date_range(start='2024-01-10', periods=32, freq='D')
    nifty_values = list(range(21000, 21032))
    nifty_df = pd.DataFrame({'close': nifty_values}, index=nifty_dates)
    nifty_df.index.name = 'date'
    
    return aqi_df, nifty_df


# ============================================================================
# Helper Functions for Test Data Generation
# ============================================================================

def generate_random_aqi_dataframe(size: int = 30, seed: int = None) -> pd.DataFrame:
    """
    Generate a random AQI DataFrame for testing.
    
    Args:
        size: Number of rows to generate
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with random AQI data
    """
    if seed is not None:
        np.random.seed(seed)
    
    dates = pd.date_range(start='2024-01-01', periods=size, freq='D')
    aqi_values = np.random.uniform(0, 500, size=size)
    df = pd.DataFrame({'aqi': aqi_values}, index=dates)
    df.index.name = 'date'
    return df


def generate_random_nifty_dataframe(size: int = 30, seed: int = None) -> pd.DataFrame:
    """
    Generate a random Nifty 50 DataFrame for testing.
    
    Args:
        size: Number of rows to generate
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with random Nifty 50 data
    """
    if seed is not None:
        np.random.seed(seed)
    
    dates = pd.date_range(start='2024-01-01', periods=size, freq='D')
    close_values = np.random.uniform(10000, 25000, size=size)
    df = pd.DataFrame({'close': close_values}, index=dates)
    df.index.name = 'date'
    return df


def create_dataframe_with_pattern(size: int = 30, pattern: str = 'linear') -> pd.DataFrame:
    """
    Create a DataFrame with a specific pattern for correlation testing.
    
    Args:
        size: Number of rows to generate
        pattern: Type of pattern ('linear', 'inverse', 'random', 'constant')
    
    Returns:
        DataFrame with 'aqi' and 'nifty_close' columns
    """
    dates = pd.date_range(start='2024-01-01', periods=size, freq='D')
    
    if pattern == 'linear':
        # Positive correlation
        aqi = np.linspace(50, 150, size)
        nifty = np.linspace(20000, 22000, size)
    elif pattern == 'inverse':
        # Negative correlation
        aqi = np.linspace(50, 150, size)
        nifty = np.linspace(22000, 20000, size)
    elif pattern == 'random':
        # No correlation
        np.random.seed(42)
        aqi = np.random.uniform(50, 150, size)
        nifty = np.random.uniform(20000, 22000, size)
    elif pattern == 'constant':
        # Constant values
        aqi = np.full(size, 100.0)
        nifty = np.full(size, 21000.0)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
    
    df = pd.DataFrame({'aqi': aqi, 'nifty_close': nifty}, index=dates)
    df.index.name = 'date'
    return df
