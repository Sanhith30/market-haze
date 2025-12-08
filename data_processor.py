"""
Data Processing Module for Market Haze

This module handles data cleaning, alignment, and statistical computations.
It provides functions to:
- Handle missing values using various strategies (forward fill, drop, interpolate)
- Align datasets from different sources to common dates
- Compute correlation coefficients between time series data

All functions work with pandas DataFrames and preserve data integrity during processing.
"""

import pandas as pd
from typing import Tuple


def handle_missing_values(df: pd.DataFrame, method: str = 'forward_fill') -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: DataFrame with potential missing values
        method: Method to handle missing values ('forward_fill', 'drop', 'interpolate')
    
    Returns:
        DataFrame with missing values handled
        
    Raises:
        ValueError: If an invalid method is specified
    """
    if method not in ['forward_fill', 'drop', 'interpolate']:
        raise ValueError(f"Invalid method '{method}'. Must be one of: 'forward_fill', 'drop', 'interpolate'")
    
    # Create a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    
    if method == 'forward_fill':
        # Forward fill: propagate last valid observation forward
        result_df = result_df.ffill()
    elif method == 'drop':
        # Drop rows with any missing values
        result_df = result_df.dropna()
    elif method == 'interpolate':
        # Interpolate missing values using linear interpolation
        # First, ensure numeric dtype for interpolation
        # If all values are None/NaN, interpolation can't work, so just return as-is
        if result_df.isna().all().all():
            # All values are missing, nothing to interpolate from
            return result_df
        result_df = result_df.interpolate(method='linear')
    
    return result_df


def align_datasets(aqi_df: pd.DataFrame, nifty_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align two datasets to common dates.
    
    This function ensures both datasets have the same date indices by performing
    an inner join. This is necessary because:
    - AQI data is available every day
    - Nifty 50 data is only available on trading days (excludes weekends/holidays)
    
    Args:
        aqi_df: DataFrame with AQI data (datetime index)
        nifty_df: DataFrame with Nifty 50 data (datetime index)
    
    Returns:
        Tuple of (aligned_aqi_df, aligned_nifty_df) with matching date indices
    """
    # Perform inner join on the date index to get only common dates
    # This ensures both DataFrames have exactly the same dates
    aligned_aqi = aqi_df.join(nifty_df, how='inner', rsuffix='_nifty')
    aligned_nifty = nifty_df.join(aqi_df, how='inner', rsuffix='_aqi')
    
    # Keep only the original columns (remove joined columns)
    # This prevents duplicate columns from the join operation
    aligned_aqi = aligned_aqi[[col for col in aligned_aqi.columns if not col.endswith('_nifty')]]
    aligned_nifty = aligned_nifty[[col for col in aligned_nifty.columns if not col.endswith('_aqi')]]
    
    return aligned_aqi, aligned_nifty


def compute_correlation(aqi_values: pd.Series, nifty_values: pd.Series) -> float:
    """
    Compute Pearson correlation coefficient between two series.
    
    The Pearson correlation coefficient measures the linear relationship between
    two variables. The result ranges from -1 to +1:
    - +1: Perfect positive correlation (both increase together)
    - 0: No linear correlation
    - -1: Perfect negative correlation (one increases as the other decreases)
    
    Args:
        aqi_values: Series of AQI values
        nifty_values: Series of Nifty 50 values
    
    Returns:
        Pearson correlation coefficient (float between -1 and 1)
    """
    # Use pandas built-in correlation method for accurate calculation
    return aqi_values.corr(nifty_values)
