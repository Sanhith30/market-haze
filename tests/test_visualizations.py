"""
Unit tests for the visualizations module.

Tests cover:
- Chart generation produces valid Plotly figures
- Charts contain expected data traces
- Chart configuration (labels, titles)
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from visualizations import create_time_series_chart, create_scatter_plot


class TestCreateTimeSeriesChart:
    """Test suite for create_time_series_chart function."""
    
    def test_returns_plotly_figure(self, sample_aqi_data):
        """Test that function returns a Plotly Figure object."""
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        assert isinstance(fig, go.Figure)
    
    def test_chart_contains_data_trace(self, sample_aqi_data):
        """Test that chart contains a data trace with correct number of points."""
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        # Check that figure has at least one trace
        assert len(fig.data) > 0
        
        # Check that trace has the same number of points as input data
        assert len(fig.data[0].x) == len(sample_aqi_data)
        assert len(fig.data[0].y) == len(sample_aqi_data)
    
    def test_chart_has_title(self, sample_aqi_data):
        """Test that chart has the specified title."""
        title = 'Mumbai AQI Time Series'
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title=title,
            y_axis_label='AQI Value',
            color='blue'
        )
        
        assert fig.layout.title.text == title
    
    def test_chart_has_axis_labels(self, sample_aqi_data):
        """Test that chart has proper axis labels."""
        y_label = 'AQI Value'
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label=y_label,
            color='blue'
        )
        
        # Check x-axis label
        assert fig.layout.xaxis.title.text == 'Date'
        
        # Check y-axis label
        assert fig.layout.yaxis.title.text == y_label
    
    def test_chart_has_hover_mode(self, sample_aqi_data):
        """Test that chart has hover mode enabled."""
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        # Check that hover mode is set
        assert fig.layout.hovermode is not None
        assert fig.layout.hovermode != ''
    
    def test_chart_data_matches_input(self, sample_aqi_data):
        """Test that chart data matches input DataFrame."""
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        # Get the trace data
        trace = fig.data[0]
        
        # Check that y values match input data
        np.testing.assert_array_equal(trace.y, sample_aqi_data['aqi'].values)
    
    def test_chart_with_custom_color(self, sample_aqi_data):
        """Test that chart uses the specified color."""
        color = 'red'
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label='AQI Value',
            color=color
        )
        
        # Check that trace uses the specified color
        assert fig.data[0].line.color == color
    
    def test_chart_with_empty_dataframe(self):
        """Test chart creation with empty DataFrame."""
        empty_df = pd.DataFrame({'aqi': []})
        empty_df.index.name = 'date'
        
        fig = create_time_series_chart(
            df=empty_df,
            value_column='aqi',
            title='Empty Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        # Should still return a valid figure
        assert isinstance(fig, go.Figure)
        
        # But with no data points
        assert len(fig.data[0].x) == 0
        assert len(fig.data[0].y) == 0


class TestCreateScatterPlot:
    """Test suite for create_scatter_plot function."""
    
    def test_returns_plotly_figure(self, sample_aqi_data, sample_nifty_data):
        """Test that function returns a Plotly Figure object."""
        # Combine data for scatter plot
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=False
        )
        
        assert isinstance(fig, go.Figure)
    
    def test_chart_contains_scatter_trace(self, sample_aqi_data, sample_nifty_data):
        """Test that chart contains scatter trace with correct number of points."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=False
        )
        
        # Check that figure has at least one trace
        assert len(fig.data) > 0
        
        # Check that trace has the same number of points as input data
        assert len(fig.data[0].x) == len(scatter_df)
        assert len(fig.data[0].y) == len(scatter_df)
    
    def test_chart_has_title(self, sample_aqi_data, sample_nifty_data):
        """Test that chart has the specified title."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        title = 'AQI vs Nifty 50 Correlation'
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title=title,
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=False
        )
        
        assert fig.layout.title.text == title
    
    def test_chart_has_axis_labels(self, sample_aqi_data, sample_nifty_data):
        """Test that chart has proper axis labels."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        x_label = 'Air Quality Index'
        y_label = 'Nifty 50 Value'
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label=x_label,
            y_axis_label=y_label,
            show_trendline=False
        )
        
        # Check axis labels
        assert fig.layout.xaxis.title.text == x_label
        assert fig.layout.yaxis.title.text == y_label
    
    def test_chart_with_trendline(self, sample_aqi_data, sample_nifty_data):
        """Test that chart includes trendline when requested."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=True
        )
        
        # Should have two traces: scatter points and trendline
        assert len(fig.data) == 2
        
        # First trace should be scatter
        assert fig.data[0].mode == 'markers'
        
        # Second trace should be line (trendline)
        assert fig.data[1].mode == 'lines'
    
    def test_chart_without_trendline(self, sample_aqi_data, sample_nifty_data):
        """Test that chart excludes trendline when not requested."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=False
        )
        
        # Should have only one trace: scatter points
        assert len(fig.data) == 1
        assert fig.data[0].mode == 'markers'
    
    def test_chart_data_matches_input(self, sample_aqi_data, sample_nifty_data):
        """Test that chart data matches input DataFrame."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=False
        )
        
        # Get the scatter trace
        trace = fig.data[0]
        
        # Check that x and y values match input data
        np.testing.assert_array_equal(trace.x, scatter_df['aqi'].values)
        np.testing.assert_array_equal(trace.y, scatter_df['nifty'].values)
    
    def test_chart_has_hover_mode(self, sample_aqi_data, sample_nifty_data):
        """Test that chart has hover mode enabled."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=False
        )
        
        # Check that hover mode is set
        assert fig.layout.hovermode is not None
        assert fig.layout.hovermode != ''


class TestChartConfiguration:
    """Test suite for chart configuration completeness."""
    
    def test_time_series_has_complete_configuration(self, sample_aqi_data):
        """Test that time series chart has all required configuration."""
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Complete Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        # Check title
        assert fig.layout.title.text is not None
        assert fig.layout.title.text != ''
        
        # Check axis labels
        assert fig.layout.xaxis.title.text is not None
        assert fig.layout.xaxis.title.text != ''
        assert fig.layout.yaxis.title.text is not None
        assert fig.layout.yaxis.title.text != ''
        
        # Check hover mode
        assert fig.layout.hovermode is not None
        assert fig.layout.hovermode != ''
    
    def test_scatter_plot_has_complete_configuration(self, sample_aqi_data, sample_nifty_data):
        """Test that scatter plot has all required configuration."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Complete Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=True
        )
        
        # Check title
        assert fig.layout.title.text is not None
        assert fig.layout.title.text != ''
        
        # Check axis labels
        assert fig.layout.xaxis.title.text is not None
        assert fig.layout.xaxis.title.text != ''
        assert fig.layout.yaxis.title.text is not None
        assert fig.layout.yaxis.title.text != ''
        
        # Check hover mode
        assert fig.layout.hovermode is not None
        assert fig.layout.hovermode != ''


class TestVisualizationDataStructure:
    """Test suite for visualization data structure validity."""
    
    def test_time_series_data_structure(self, sample_aqi_data):
        """Test that time series chart has valid data structure."""
        fig = create_time_series_chart(
            df=sample_aqi_data,
            value_column='aqi',
            title='Test Chart',
            y_axis_label='AQI Value',
            color='blue'
        )
        
        # Check that figure has data
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Check that trace has x and y data
        trace = fig.data[0]
        assert hasattr(trace, 'x')
        assert hasattr(trace, 'y')
        assert len(trace.x) == len(sample_aqi_data)
        assert len(trace.y) == len(sample_aqi_data)
    
    def test_scatter_plot_data_structure(self, sample_aqi_data, sample_nifty_data):
        """Test that scatter plot has valid data structure."""
        scatter_df = pd.DataFrame({
            'aqi': sample_aqi_data['aqi'],
            'nifty': sample_nifty_data['close']
        })
        
        fig = create_scatter_plot(
            df=scatter_df,
            x_column='aqi',
            y_column='nifty',
            title='Test Scatter',
            x_axis_label='AQI',
            y_axis_label='Nifty 50',
            show_trendline=True
        )
        
        # Check that figure has data
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Check scatter trace
        scatter_trace = fig.data[0]
        assert hasattr(scatter_trace, 'x')
        assert hasattr(scatter_trace, 'y')
        assert len(scatter_trace.x) == len(scatter_df)
        assert len(scatter_trace.y) == len(scatter_df)
        
        # Check trendline trace if present
        if len(fig.data) > 1:
            trendline_trace = fig.data[1]
            assert hasattr(trendline_trace, 'x')
            assert hasattr(trendline_trace, 'y')
            assert len(trendline_trace.x) > 0
            assert len(trendline_trace.y) > 0
