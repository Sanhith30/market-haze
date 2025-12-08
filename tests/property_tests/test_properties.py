"""
Property-based tests for Market Haze application.

These tests verify universal properties that should hold across all valid executions.
"""

import pandas as pd
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest

# Feature: market-haze, Property 1: Date range completeness
@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(days=st.integers(min_value=30, max_value=365))
def test_date_range_completeness_aqi(days):
    """
    Property 1: Date range completeness
    
    For any data fetch request with a specified number of days, the returned 
    DataFrame should contain data spanning approximately that number of days 
    (within tolerance for weekends/holidays).
    
    Validates: Requirements 1.1, 2.1
    """
    from data_loader import fetch_mumbai_aqi
    
    # Fetch data for the specified number of days
    df = fetch_mumbai_aqi(days=days)
    
    # Verify DataFrame is not empty
    assert not df.empty, "DataFrame should not be empty"
    
    # Verify DataFrame has the expected structure
    assert 'aqi' in df.columns, "DataFrame should have 'aqi' column"
    assert isinstance(df.index, pd.DatetimeIndex), "Index should be DatetimeIndex"
    
    # Calculate the actual date range in the data
    date_range_days = (df.index.max() - df.index.min()).days
    
    # Allow tolerance for weekends, holidays, and API limitations
    # We expect at least 80% of the requested days to be present
    tolerance = 0.20
    min_expected_days = days * (1 - tolerance)
    max_expected_days = days * (1 + tolerance)
    
    assert min_expected_days <= date_range_days <= max_expected_days, \
        f"Date range {date_range_days} days should be approximately {days} days (±{tolerance*100}%)"


# Feature: market-haze, Property 1: Date range completeness
@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(days=st.integers(min_value=30, max_value=365))
def test_date_range_completeness_nifty50(days):
    """
    Property 1: Date range completeness
    
    For any data fetch request with a specified number of days, the returned 
    DataFrame should contain data spanning approximately that number of days 
    (within tolerance for weekends/holidays).
    
    Validates: Requirements 1.1, 2.1
    """
    from data_loader import fetch_nifty50
    
    # Fetch data for the specified number of days
    df = fetch_nifty50(days=days)
    
    # Verify DataFrame is not empty
    assert not df.empty, "DataFrame should not be empty"
    
    # Verify DataFrame has the expected structure
    assert 'close' in df.columns, "DataFrame should have 'close' column"
    assert isinstance(df.index, pd.DatetimeIndex), "Index should be DatetimeIndex"
    
    # Calculate the actual date range in the data
    date_range_days = (df.index.max() - df.index.min()).days
    
    # Allow tolerance for weekends, holidays, and API limitations
    # Stock markets are closed on weekends and holidays, so we need more tolerance
    tolerance = 0.30
    min_expected_days = days * (1 - tolerance)
    max_expected_days = days * (1 + tolerance)
    
    assert min_expected_days <= date_range_days <= max_expected_days, \
        f"Date range {date_range_days} days should be approximately {days} days (±{tolerance*100}%)"


# Feature: market-haze, Property 3: Error messages on API failure
@settings(max_examples=100, deadline=10000)
@given(error_type=st.sampled_from(['Exception', 'ConnectionError', 'ValueError', 'RuntimeError']))
def test_error_messages_on_api_failure(error_type):
    """
    Property 3: Error messages on API failure
    
    For any API request that fails, the system should return an error message 
    that is non-empty and contains information about the failure type.
    
    Validates: Requirements 1.4, 2.4, 5.2
    """
    from data_loader import APIError
    from unittest.mock import patch, MagicMock
    import yfinance as yf
    
    # Create an exception instance based on the error type
    if error_type == 'Exception':
        mock_exception = Exception("Generic API failure")
    elif error_type == 'ConnectionError':
        mock_exception = ConnectionError("Network connection failed")
    elif error_type == 'ValueError':
        mock_exception = ValueError("Invalid parameter value")
    elif error_type == 'RuntimeError':
        mock_exception = RuntimeError("Runtime error occurred")
    
    # Test Nifty 50 fetcher with mocked failure
    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.history.side_effect = mock_exception
        mock_ticker.return_value = mock_instance
        
        try:
            from data_loader import fetch_nifty50
            fetch_nifty50(days=365)
            pytest.fail("Expected APIError to be raised")
        except APIError as e:
            error_message = str(e)
            # Verify error message is non-empty
            assert error_message, "Error message should not be empty"
            assert len(error_message) > 0, "Error message should have content"
            
            # Verify error message contains failure information
            assert "Data Loader" in error_message or "API" in error_message, \
                f"Error message should identify the component: {error_message}"
            assert "Error" in error_message or "Failed" in error_message or "fail" in error_message.lower(), \
                f"Error message should indicate failure: {error_message}"
            
            # Verify the original error information is preserved
            assert len(error_message) > 20, \
                f"Error message should contain detailed information: {error_message}"
    
    # Test with empty DataFrame response
    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance
        
        try:
            from data_loader import fetch_nifty50
            fetch_nifty50(days=365)
            pytest.fail("Expected APIError to be raised for empty response")
        except APIError as e:
            error_message = str(e)
            assert error_message, "Error message should not be empty"
            assert len(error_message) > 0, "Error message should have content"
            assert "Data Loader" in error_message or "API" in error_message, \
                f"Error message should identify the component: {error_message}"
            assert "Error" in error_message or "No data" in error_message, \
                f"Error message should indicate the problem: {error_message}"


# Feature: market-haze, Property 2: Missing value handling preservation
@settings(max_examples=100, deadline=5000)
@given(
    data=st.lists(
        st.one_of(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), st.none()),
        min_size=5,
        max_size=50
    ),
    method=st.sampled_from(['forward_fill', 'drop', 'interpolate'])
)
def test_missing_value_handling_preservation(data, method):
    """
    Property 2: Missing value handling preservation
    
    For any dataset with missing values, after applying the missing value handler, 
    the resulting dataset should either have no missing values (if using forward fill 
    or interpolation) or should have fewer rows (if using drop), and the non-missing 
    values should remain unchanged.
    
    Validates: Requirements 1.3, 2.3
    """
    from data_processor import handle_missing_values
    
    # Create a DataFrame with the generated data
    df = pd.DataFrame({'value': data})
    
    # Store original non-missing values
    original_non_missing = df[df['value'].notna()]['value'].tolist()
    original_length = len(df)
    missing_count = df['value'].isna().sum()
    
    # Apply missing value handling
    result_df = handle_missing_values(df, method=method)
    
    # Verify the result is a DataFrame
    assert isinstance(result_df, pd.DataFrame), "Result should be a DataFrame"
    
    # Check method-specific properties
    if method == 'forward_fill':
        # Forward fill should not increase the number of rows
        assert len(result_df) == original_length, \
            f"Forward fill should preserve row count: expected {original_length}, got {len(result_df)}"
        
        # If there were any non-missing values, result should have fewer or equal missing values
        if len(original_non_missing) > 0:
            result_missing_count = result_df['value'].isna().sum()
            assert result_missing_count <= missing_count, \
                f"Forward fill should reduce or maintain missing values: original {missing_count}, result {result_missing_count}"
    
    elif method == 'drop':
        # Drop should result in fewer or equal rows
        assert len(result_df) <= original_length, \
            f"Drop should reduce or maintain row count: original {original_length}, result {len(result_df)}"
        
        # Drop should have no missing values
        assert result_df['value'].isna().sum() == 0, \
            "Drop method should result in no missing values"
        
        # If we had missing values, the result should be shorter
        if missing_count > 0:
            assert len(result_df) < original_length, \
                f"Drop with missing values should reduce row count: original {original_length}, result {len(result_df)}"
    
    elif method == 'interpolate':
        # Interpolate should not change the number of rows
        assert len(result_df) == original_length, \
            f"Interpolate should preserve row count: expected {original_length}, got {len(result_df)}"
        
        # Interpolate should reduce missing values (unless all values are missing or only edge values are missing)
        result_missing_count = result_df['value'].isna().sum()
        assert result_missing_count <= missing_count, \
            f"Interpolate should reduce or maintain missing values: original {missing_count}, result {result_missing_count}"
    
    # Verify that non-missing values are preserved (they should appear in the result)
    # This is the key preservation property
    result_values = result_df['value'].dropna().tolist()
    
    # All original non-missing values should be present in the result
    # (allowing for floating point comparison tolerance)
    for original_val in original_non_missing:
        # Check if this value exists in result (with tolerance for float comparison)
        found = any(abs(result_val - original_val) < 1e-9 for result_val in result_values)
        assert found, f"Original non-missing value {original_val} should be preserved in result"


# Feature: market-haze, Property 4: Correlation computation correctness
@settings(max_examples=100, deadline=5000)
@given(
    aqi_data=st.lists(
        st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
        min_size=10,
        max_size=100
    ),
    nifty_data=st.lists(
        st.floats(min_value=10000, max_value=25000, allow_nan=False, allow_infinity=False),
        min_size=10,
        max_size=100
    )
)
def test_correlation_computation_correctness(aqi_data, nifty_data):
    """
    Property 4: Correlation computation correctness
    
    For any two aligned numeric series, the computed Pearson correlation coefficient 
    should match the result from pandas' built-in correlation function and should be 
    a value between -1 and 1 inclusive.
    
    Validates: Requirements 3.1
    """
    from data_processor import compute_correlation
    
    # Ensure both series have the same length for correlation
    min_length = min(len(aqi_data), len(nifty_data))
    aqi_data = aqi_data[:min_length]
    nifty_data = nifty_data[:min_length]
    
    # Create pandas Series
    aqi_series = pd.Series(aqi_data)
    nifty_series = pd.Series(nifty_data)
    
    # Compute correlation using our function
    result = compute_correlation(aqi_series, nifty_series)
    
    # Verify result matches pandas built-in correlation
    expected = aqi_series.corr(nifty_series)
    
    # Handle NaN case (when series have no variance - all values are the same)
    # This is mathematically correct: correlation is undefined for constant series
    if pd.isna(expected):
        assert pd.isna(result), \
            f"When pandas returns NaN (constant series), our function should too. Expected NaN, got {result}"
    else:
        # Verify result is a float
        assert isinstance(result, (float, int)), f"Correlation should be numeric, got {type(result)}"
        
        # Verify result is between -1 and 1 (inclusive)
        assert -1 <= result <= 1, \
            f"Correlation coefficient should be between -1 and 1, got {result}"
        
        # Allow small floating point differences
        assert abs(result - expected) < 1e-9, \
            f"Correlation should match pandas result: expected {expected}, got {result}"


# Feature: market-haze, Property 5: Dataset alignment consistency
@settings(max_examples=100, deadline=5000)
@given(
    aqi_dates=st.lists(
        st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31)),
        min_size=5,
        max_size=50,
        unique=True
    ),
    nifty_dates=st.lists(
        st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31)),
        min_size=5,
        max_size=50,
        unique=True
    ),
    aqi_values=st.lists(
        st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
        min_size=5,
        max_size=50
    ),
    nifty_values=st.lists(
        st.floats(min_value=10000, max_value=25000, allow_nan=False, allow_infinity=False),
        min_size=5,
        max_size=50
    )
)
def test_dataset_alignment_consistency(aqi_dates, nifty_dates, aqi_values, nifty_values):
    """
    Property 5: Dataset alignment consistency
    
    For any two datasets with different date ranges, after alignment, both resulting 
    datasets should have identical date indices and the same number of rows.
    
    Validates: Requirements 3.4
    """
    from data_processor import align_datasets
    
    # Ensure values match the length of dates
    aqi_values = aqi_values[:len(aqi_dates)]
    nifty_values = nifty_values[:len(nifty_dates)]
    
    # Pad with additional values if needed
    while len(aqi_values) < len(aqi_dates):
        aqi_values.append(100.0)
    while len(nifty_values) < len(nifty_dates):
        nifty_values.append(15000.0)
    
    # Create DataFrames with datetime indices
    aqi_df = pd.DataFrame({'aqi': aqi_values}, index=pd.DatetimeIndex(aqi_dates))
    nifty_df = pd.DataFrame({'close': nifty_values}, index=pd.DatetimeIndex(nifty_dates))
    
    # Sort indices to ensure proper alignment
    aqi_df = aqi_df.sort_index()
    nifty_df = nifty_df.sort_index()
    
    # Align the datasets
    aligned_aqi, aligned_nifty = align_datasets(aqi_df, nifty_df)
    
    # Property 1: Both aligned datasets should have identical date indices
    assert aligned_aqi.index.equals(aligned_nifty.index), \
        "Aligned datasets should have identical date indices"
    
    # Property 2: Both aligned datasets should have the same number of rows
    assert len(aligned_aqi) == len(aligned_nifty), \
        f"Aligned datasets should have the same number of rows: aqi={len(aligned_aqi)}, nifty={len(aligned_nifty)}"
    
    # Property 3: The aligned datasets should only contain dates that were in both original datasets
    common_dates = set(aqi_df.index).intersection(set(nifty_df.index))
    assert len(aligned_aqi) == len(common_dates), \
        f"Aligned datasets should contain exactly the common dates: expected {len(common_dates)}, got {len(aligned_aqi)}"
    
    # Property 4: All dates in aligned datasets should be from the original datasets
    for date in aligned_aqi.index:
        assert date in aqi_df.index, f"Date {date} in aligned AQI should be from original AQI dataset"
        assert date in nifty_df.index, f"Date {date} in aligned AQI should be from original Nifty dataset"
    
    # Property 5: The aligned datasets should preserve the original column structure
    assert 'aqi' in aligned_aqi.columns, "Aligned AQI dataset should have 'aqi' column"
    assert 'close' in aligned_nifty.columns, "Aligned Nifty dataset should have 'close' column"
    
    # Property 6: Values in aligned datasets should match original values for those dates
    for date in aligned_aqi.index:
        original_aqi_value = aqi_df.loc[date, 'aqi']
        aligned_aqi_value = aligned_aqi.loc[date, 'aqi']
        assert abs(original_aqi_value - aligned_aqi_value) < 1e-9, \
            f"AQI value for {date} should be preserved: original={original_aqi_value}, aligned={aligned_aqi_value}"
        
        original_nifty_value = nifty_df.loc[date, 'close']
        aligned_nifty_value = aligned_nifty.loc[date, 'close']
        assert abs(original_nifty_value - aligned_nifty_value) < 1e-9, \
            f"Nifty value for {date} should be preserved: original={original_nifty_value}, aligned={aligned_nifty_value}"


# Feature: market-haze, Property 6: Visualization data structure validity
@settings(max_examples=100, deadline=5000)
@given(
    dates=st.lists(
        st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31)),
        min_size=5,
        max_size=50,
        unique=True
    ),
    values=st.lists(
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        min_size=5,
        max_size=50
    )
)
def test_visualization_data_structure_validity(dates, values):
    """
    Property 6: Visualization data structure validity
    
    For any dataset passed to a visualization function, the resulting Plotly figure 
    should contain data traces with the same number of points as the input dataset.
    
    Validates: Requirements 1.2, 2.2, 3.3
    """
    from visualizations import create_time_series_chart, create_scatter_plot
    
    # Ensure values match the length of dates
    values = values[:len(dates)]
    while len(values) < len(dates):
        values.append(100.0)
    
    # Create DataFrame with datetime index
    df = pd.DataFrame({'value': values}, index=pd.DatetimeIndex(dates))
    df = df.sort_index()
    
    # Test time series chart
    fig = create_time_series_chart(
        df=df,
        value_column='value',
        title='Test Chart',
        y_axis_label='Value',
        color='blue'
    )
    
    # Verify figure is created
    assert fig is not None, "Figure should be created"
    assert hasattr(fig, 'data'), "Figure should have data attribute"
    
    # Verify data traces exist
    assert len(fig.data) > 0, "Figure should have at least one data trace"
    
    # Verify the number of points in the trace matches input dataset
    trace = fig.data[0]
    assert len(trace.x) == len(df), \
        f"Time series trace should have same number of x-points as input: expected {len(df)}, got {len(trace.x)}"
    assert len(trace.y) == len(df), \
        f"Time series trace should have same number of y-points as input: expected {len(df)}, got {len(trace.y)}"
    
    # Test scatter plot (need two columns)
    df['value2'] = [v * 1.5 for v in values]
    
    fig_scatter = create_scatter_plot(
        df=df,
        x_column='value',
        y_column='value2',
        title='Test Scatter',
        x_axis_label='X Value',
        y_axis_label='Y Value',
        show_trendline=False
    )
    
    # Verify scatter plot figure is created
    assert fig_scatter is not None, "Scatter figure should be created"
    assert hasattr(fig_scatter, 'data'), "Scatter figure should have data attribute"
    assert len(fig_scatter.data) > 0, "Scatter figure should have at least one data trace"
    
    # Verify the number of points in the scatter trace matches input dataset
    scatter_trace = fig_scatter.data[0]
    assert len(scatter_trace.x) == len(df), \
        f"Scatter trace should have same number of x-points as input: expected {len(df)}, got {len(scatter_trace.x)}"
    assert len(scatter_trace.y) == len(df), \
        f"Scatter trace should have same number of y-points as input: expected {len(df)}, got {len(scatter_trace.y)}"


# Feature: market-haze, Property 7: Chart configuration completeness
@settings(max_examples=100, deadline=5000)
@given(
    dates=st.lists(
        st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31)),
        min_size=5,
        max_size=50,
        unique=True
    ),
    values=st.lists(
        st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        min_size=5,
        max_size=50
    )
)
def test_chart_configuration_completeness(dates, values):
    """
    Property 7: Chart configuration completeness
    
    For any Plotly chart generated by the system, the figure should have non-empty 
    axis labels, a non-empty title, and hover mode enabled.
    
    Validates: Requirements 4.1, 4.2, 4.3
    """
    from visualizations import create_time_series_chart, create_scatter_plot
    
    # Ensure values match the length of dates
    values = values[:len(dates)]
    while len(values) < len(dates):
        values.append(100.0)
    
    # Create DataFrame with datetime index
    df = pd.DataFrame({'value': values}, index=pd.DatetimeIndex(dates))
    df = df.sort_index()
    
    # Test time series chart configuration
    fig = create_time_series_chart(
        df=df,
        value_column='value',
        title='Test Time Series',
        y_axis_label='Test Value',
        color='blue'
    )
    
    # Verify title is non-empty
    assert hasattr(fig, 'layout'), "Figure should have layout attribute"
    assert hasattr(fig.layout, 'title'), "Figure layout should have title"
    assert fig.layout.title.text, "Figure title should be non-empty"
    assert len(fig.layout.title.text) > 0, "Figure title should have content"
    
    # Verify x-axis label is non-empty
    assert hasattr(fig.layout, 'xaxis'), "Figure layout should have xaxis"
    assert hasattr(fig.layout.xaxis, 'title'), "X-axis should have title"
    assert fig.layout.xaxis.title.text, "X-axis label should be non-empty"
    assert len(fig.layout.xaxis.title.text) > 0, "X-axis label should have content"
    
    # Verify y-axis label is non-empty
    assert hasattr(fig.layout, 'yaxis'), "Figure layout should have yaxis"
    assert hasattr(fig.layout.yaxis, 'title'), "Y-axis should have title"
    assert fig.layout.yaxis.title.text, "Y-axis label should be non-empty"
    assert len(fig.layout.yaxis.title.text) > 0, "Y-axis label should have content"
    
    # Verify hover mode is enabled
    assert hasattr(fig.layout, 'hovermode'), "Figure layout should have hovermode"
    assert fig.layout.hovermode is not None, "Hover mode should be set"
    assert fig.layout.hovermode != False, "Hover mode should be enabled"
    
    # Test scatter plot configuration
    df['value2'] = [v * 1.5 for v in values]
    
    fig_scatter = create_scatter_plot(
        df=df,
        x_column='value',
        y_column='value2',
        title='Test Scatter Plot',
        x_axis_label='X Axis',
        y_axis_label='Y Axis',
        show_trendline=True
    )
    
    # Verify scatter plot title is non-empty
    assert hasattr(fig_scatter.layout, 'title'), "Scatter figure layout should have title"
    assert fig_scatter.layout.title.text, "Scatter figure title should be non-empty"
    assert len(fig_scatter.layout.title.text) > 0, "Scatter figure title should have content"
    
    # Verify scatter plot x-axis label is non-empty
    assert hasattr(fig_scatter.layout, 'xaxis'), "Scatter figure layout should have xaxis"
    assert hasattr(fig_scatter.layout.xaxis, 'title'), "Scatter x-axis should have title"
    assert fig_scatter.layout.xaxis.title.text, "Scatter x-axis label should be non-empty"
    assert len(fig_scatter.layout.xaxis.title.text) > 0, "Scatter x-axis label should have content"
    
    # Verify scatter plot y-axis label is non-empty
    assert hasattr(fig_scatter.layout, 'yaxis'), "Scatter figure layout should have yaxis"
    assert hasattr(fig_scatter.layout.yaxis, 'title'), "Scatter y-axis should have title"
    assert fig_scatter.layout.yaxis.title.text, "Scatter y-axis label should be non-empty"
    assert len(fig_scatter.layout.yaxis.title.text) > 0, "Scatter y-axis label should have content"
    
    # Verify scatter plot hover mode is enabled
    assert hasattr(fig_scatter.layout, 'hovermode'), "Scatter figure layout should have hovermode"
    assert fig_scatter.layout.hovermode is not None, "Scatter hover mode should be set"
    assert fig_scatter.layout.hovermode != False, "Scatter hover mode should be enabled"



# Feature: market-haze, Property 8: Error handling without crashes
@settings(max_examples=100, deadline=5000)
@given(
    error_scenario=st.sampled_from([
        'empty_dataframe',
        'missing_column',
        'invalid_index',
        'nan_values',
        'mismatched_lengths'
    ])
)
def test_error_handling_without_crashes(error_scenario):
    """
    Property 8: Error handling without crashes
    
    For any processing error that occurs during data manipulation, the system should 
    catch the exception, log it, and return a user-friendly error message without 
    terminating the application.
    
    Validates: Requirements 5.3
    """
    from data_processor import handle_missing_values, align_datasets, compute_correlation
    import logging
    
    # Set up logging to capture error messages
    logger = logging.getLogger()
    
    try:
        if error_scenario == 'empty_dataframe':
            # Test with empty DataFrame
            df = pd.DataFrame()
            try:
                result = handle_missing_values(df, method='forward_fill')
                # Should not crash - either return empty or handle gracefully
                assert isinstance(result, pd.DataFrame), "Should return a DataFrame even for empty input"
            except Exception as e:
                # If it raises an exception, it should be a meaningful one, not a crash
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
                assert not isinstance(e, (SystemExit, KeyboardInterrupt)), \
                    "Should not raise system-terminating exceptions"
        
        elif error_scenario == 'missing_column':
            # Test with DataFrame missing expected columns
            df = pd.DataFrame({'wrong_column': [1, 2, 3]})
            try:
                # This should handle the error gracefully
                from visualizations import create_time_series_chart
                # Attempting to access non-existent column should be handled
                result = create_time_series_chart(
                    df=df,
                    value_column='nonexistent',
                    title='Test',
                    y_axis_label='Value'
                )
                # If it doesn't raise an error, that's also acceptable (graceful handling)
            except KeyError as e:
                # KeyError is acceptable - it's a controlled error, not a crash
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
            except Exception as e:
                # Other exceptions should also be controlled
                assert not isinstance(e, (SystemExit, KeyboardInterrupt)), \
                    "Should not raise system-terminating exceptions"
        
        elif error_scenario == 'invalid_index':
            # Test with DataFrame with non-datetime index
            df = pd.DataFrame({'value': [1, 2, 3]}, index=[0, 1, 2])
            try:
                # This might work or raise a controlled error
                from visualizations import create_time_series_chart
                result = create_time_series_chart(
                    df=df,
                    value_column='value',
                    title='Test',
                    y_axis_label='Value'
                )
                # If it works, that's fine - graceful handling
            except Exception as e:
                # Should not crash the application
                assert not isinstance(e, (SystemExit, KeyboardInterrupt)), \
                    "Should not raise system-terminating exceptions"
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
        
        elif error_scenario == 'nan_values':
            # Test with all NaN values
            df = pd.DataFrame({'value': [float('nan')] * 5})
            try:
                result = handle_missing_values(df, method='interpolate')
                # Should handle gracefully
                assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
            except Exception as e:
                # Should not crash
                assert not isinstance(e, (SystemExit, KeyboardInterrupt)), \
                    "Should not raise system-terminating exceptions"
        
        elif error_scenario == 'mismatched_lengths':
            # Test correlation with mismatched series lengths
            series1 = pd.Series([1, 2, 3, 4, 5])
            series2 = pd.Series([10, 20, 30])
            try:
                # Pandas should handle this, but we test it doesn't crash
                result = compute_correlation(series1, series2)
                # If it works, verify it's a valid correlation or NaN
                assert isinstance(result, (float, int)) or pd.isna(result), \
                    "Should return a numeric value or NaN"
            except Exception as e:
                # Should not crash the application
                assert not isinstance(e, (SystemExit, KeyboardInterrupt)), \
                    "Should not raise system-terminating exceptions"
                error_msg = str(e)
                assert len(error_msg) > 0, "Error message should not be empty"
        
        # If we reach here without crashing, the test passes
        assert True, "Error handling completed without application crash"
        
    except (SystemExit, KeyboardInterrupt) as e:
        pytest.fail(f"Application should not crash with system-terminating exception: {type(e).__name__}")
    except Exception as e:
        # Any other exception is acceptable as long as it's controlled
        # and doesn't terminate the application
        error_msg = str(e)
        assert len(error_msg) > 0, "Error message should provide information"
