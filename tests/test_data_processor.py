"""
Unit tests for the data_processor module.

Tests cover:
- Dataset alignment with sample datasets
- Correlation computation with known input/output pairs
- Missing value handling with specific examples
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from data_processor import handle_missing_values, align_datasets, compute_correlation


class TestHandleMissingValues:
    """Test suite for handle_missing_values function."""
    
    def test_forward_fill_method(self, sample_aqi_with_missing):
        """Test forward fill method propagates last valid value."""
        result = handle_missing_values(sample_aqi_with_missing, method='forward_fill')
        
        # Check that no NaN values remain
        assert not result['aqi'].isna().any()
        
        # Check that first value is preserved (it's not NaN)
        assert result['aqi'].iloc[0] == sample_aqi_with_missing['aqi'].iloc[0]
        
        # Check that forward fill worked correctly
        # Second value should be filled with first value
        assert result['aqi'].iloc[1] == sample_aqi_with_missing['aqi'].iloc[0]
    
    def test_drop_method(self, sample_aqi_with_missing):
        """Test drop method removes rows with missing values."""
        original_length = len(sample_aqi_with_missing)
        result = handle_missing_values(sample_aqi_with_missing, method='drop')
        
        # Check that no NaN values remain
        assert not result['aqi'].isna().any()
        
        # Check that result has fewer rows
        assert len(result) < original_length
        
        # Check that all remaining values are from the original
        for val in result['aqi']:
            assert val in sample_aqi_with_missing['aqi'].values
    
    def test_interpolate_method(self, sample_aqi_with_missing):
        """Test interpolate method fills missing values with linear interpolation."""
        result = handle_missing_values(sample_aqi_with_missing, method='interpolate')
        
        # Check that no NaN values remain (except possibly at edges)
        # Interpolation might leave NaN at the start if first value is NaN
        # In our test data, first value is not NaN, so all should be filled
        assert not result['aqi'].isna().any()
    
    def test_invalid_method_raises_error(self, sample_aqi_data):
        """Test that invalid method raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            handle_missing_values(sample_aqi_data, method='invalid_method')
        
        assert "Invalid method" in str(exc_info.value)
    
    def test_preserves_non_missing_values(self, sample_aqi_with_missing):
        """Test that non-missing values are preserved."""
        result = handle_missing_values(sample_aqi_with_missing, method='forward_fill')
        
        # Get indices where original data was not NaN
        non_nan_mask = ~sample_aqi_with_missing['aqi'].isna()
        
        # Check that these values are preserved
        original_non_nan = sample_aqi_with_missing.loc[non_nan_mask, 'aqi']
        result_non_nan = result.loc[non_nan_mask, 'aqi']
        
        pd.testing.assert_series_equal(original_non_nan, result_non_nan)
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame({'aqi': []})
        result = handle_missing_values(empty_df, method='forward_fill')
        
        assert len(result) == 0
        assert 'aqi' in result.columns
    
    def test_all_missing_values(self):
        """Test handling of DataFrame with all missing values."""
        dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
        all_nan_df = pd.DataFrame({'aqi': [np.nan] * 5}, index=dates)
        
        # Forward fill on all NaN should still have NaN
        result = handle_missing_values(all_nan_df, method='forward_fill')
        assert result['aqi'].isna().all()
        
        # Drop should result in empty DataFrame
        result_drop = handle_missing_values(all_nan_df, method='drop')
        assert len(result_drop) == 0


class TestAlignDatasets:
    """Test suite for align_datasets function."""
    
    def test_alignment_with_overlapping_dates(self, sample_misaligned_data):
        """Test alignment with partially overlapping date ranges."""
        aqi_df, nifty_df = sample_misaligned_data
        
        aligned_aqi, aligned_nifty = align_datasets(aqi_df, nifty_df)
        
        # Check that both have the same indices
        assert aligned_aqi.index.equals(aligned_nifty.index)
        
        # Check that both have the same length
        assert len(aligned_aqi) == len(aligned_nifty)
        
        # Check that only overlapping dates remain
        # Original AQI: Jan 1-25, Nifty: Jan 10-Feb 10
        # Overlap should be Jan 10-25 (16 days)
        assert len(aligned_aqi) == 16
    
    def test_alignment_preserves_column_names(self, sample_aqi_data, sample_nifty_data):
        """Test that alignment preserves original column names."""
        aligned_aqi, aligned_nifty = align_datasets(sample_aqi_data, sample_nifty_data)
        
        # Check that primary columns exist
        assert 'aqi' in aligned_aqi.columns
        assert 'close' in aligned_nifty.columns
        
        # The function joins dataframes, so both may have both columns
        # This is acceptable as long as the primary column is present
    
    def test_alignment_with_identical_dates(self, sample_aqi_data, sample_nifty_data):
        """Test alignment when both DataFrames have identical dates."""
        # Both fixtures have the same date range
        aligned_aqi, aligned_nifty = align_datasets(sample_aqi_data, sample_nifty_data)
        
        # Should have all dates
        assert len(aligned_aqi) == len(sample_aqi_data)
        assert len(aligned_nifty) == len(sample_nifty_data)
    
    def test_alignment_with_no_overlap(self):
        """Test alignment when there's no date overlap."""
        # Create two DataFrames with no overlapping dates
        aqi_dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        nifty_dates = pd.date_range(start='2024-02-01', periods=10, freq='D')
        
        aqi_df = pd.DataFrame({'aqi': range(10)}, index=aqi_dates)
        nifty_df = pd.DataFrame({'close': range(10)}, index=nifty_dates)
        
        aligned_aqi, aligned_nifty = align_datasets(aqi_df, nifty_df)
        
        # Should result in empty DataFrames
        assert len(aligned_aqi) == 0
        assert len(aligned_nifty) == 0
    
    def test_alignment_preserves_data_values(self, sample_aqi_data, sample_nifty_data):
        """Test that alignment preserves the actual data values."""
        aligned_aqi, aligned_nifty = align_datasets(sample_aqi_data, sample_nifty_data)
        
        # Check that values match for common dates
        for date in aligned_aqi.index:
            assert aligned_aqi.loc[date, 'aqi'] == sample_aqi_data.loc[date, 'aqi']
            assert aligned_nifty.loc[date, 'close'] == sample_nifty_data.loc[date, 'close']


class TestComputeCorrelation:
    """Test suite for compute_correlation function."""
    
    def test_perfect_positive_correlation(self):
        """Test correlation with perfectly correlated data."""
        # Create two series with perfect positive correlation
        values1 = pd.Series([1, 2, 3, 4, 5])
        values2 = pd.Series([2, 4, 6, 8, 10])
        
        correlation = compute_correlation(values1, values2)
        
        # Should be very close to 1.0
        assert abs(correlation - 1.0) < 0.0001
    
    def test_perfect_negative_correlation(self):
        """Test correlation with perfectly negatively correlated data."""
        # Create two series with perfect negative correlation
        values1 = pd.Series([1, 2, 3, 4, 5])
        values2 = pd.Series([10, 8, 6, 4, 2])
        
        correlation = compute_correlation(values1, values2)
        
        # Should be very close to -1.0
        assert abs(correlation - (-1.0)) < 0.0001
    
    def test_no_correlation(self):
        """Test correlation with uncorrelated data."""
        # Create two series with no correlation
        np.random.seed(42)
        values1 = pd.Series(np.random.randn(100))
        values2 = pd.Series(np.random.randn(100))
        
        correlation = compute_correlation(values1, values2)
        
        # Should be close to 0 (but not exactly due to randomness)
        assert abs(correlation) < 0.3  # Loose bound for random data
    
    def test_correlation_range(self, sample_aqi_data, sample_nifty_data):
        """Test that correlation is always between -1 and 1."""
        correlation = compute_correlation(
            sample_aqi_data['aqi'],
            sample_nifty_data['close']
        )
        
        # Correlation must be in [-1, 1]
        assert -1.0 <= correlation <= 1.0
    
    def test_correlation_with_constant_values(self):
        """Test correlation when one series has constant values."""
        values1 = pd.Series([5, 5, 5, 5, 5])
        values2 = pd.Series([1, 2, 3, 4, 5])
        
        correlation = compute_correlation(values1, values2)
        
        # Correlation with constant series should be NaN
        assert pd.isna(correlation)
    
    def test_correlation_matches_pandas_builtin(self, sample_aqi_data, sample_nifty_data):
        """Test that our correlation matches pandas built-in correlation."""
        our_correlation = compute_correlation(
            sample_aqi_data['aqi'],
            sample_nifty_data['close']
        )
        
        pandas_correlation = sample_aqi_data['aqi'].corr(sample_nifty_data['close'])
        
        # Should match exactly (or very close due to floating point)
        assert abs(our_correlation - pandas_correlation) < 0.0001
    
    def test_correlation_with_known_values(self):
        """Test correlation with known input/output pairs."""
        # Known example: correlation between [1,2,3] and [1,2,3] is 1.0
        values1 = pd.Series([1, 2, 3])
        values2 = pd.Series([1, 2, 3])
        
        correlation = compute_correlation(values1, values2)
        assert abs(correlation - 1.0) < 0.0001
        
        # Known example: correlation between [1,2,3] and [3,2,1] is -1.0
        values3 = pd.Series([1, 2, 3])
        values4 = pd.Series([3, 2, 1])
        
        correlation2 = compute_correlation(values3, values4)
        assert abs(correlation2 - (-1.0)) < 0.0001


class TestIntegration:
    """Integration tests for data processor functions."""
    
    def test_full_pipeline(self, sample_aqi_with_missing, sample_nifty_with_missing):
        """Test the full data processing pipeline."""
        # Step 1: Handle missing values
        aqi_clean = handle_missing_values(sample_aqi_with_missing, method='forward_fill')
        nifty_clean = handle_missing_values(sample_nifty_with_missing, method='forward_fill')
        
        # Step 2: Align datasets
        aligned_aqi, aligned_nifty = align_datasets(aqi_clean, nifty_clean)
        
        # Step 3: Compute correlation
        correlation = compute_correlation(aligned_aqi['aqi'], aligned_nifty['close'])
        
        # Verify results
        assert not aligned_aqi['aqi'].isna().any()
        assert not aligned_nifty['close'].isna().any()
        assert aligned_aqi.index.equals(aligned_nifty.index)
        assert -1.0 <= correlation <= 1.0
    
    def test_pipeline_with_different_methods(self, sample_aqi_with_missing, sample_nifty_with_missing):
        """Test pipeline with different missing value handling methods."""
        # Test with drop method
        aqi_clean = handle_missing_values(sample_aqi_with_missing, method='drop')
        nifty_clean = handle_missing_values(sample_nifty_with_missing, method='drop')
        
        aligned_aqi, aligned_nifty = align_datasets(aqi_clean, nifty_clean)
        
        if len(aligned_aqi) > 0:  # Only compute if we have data
            correlation = compute_correlation(aligned_aqi['aqi'], aligned_nifty['close'])
            assert -1.0 <= correlation <= 1.0
