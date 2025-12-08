"""
Visualization Module for Market Haze

This module provides functions for generating Plotly charts for data visualization.
It creates interactive charts with features like:
- Zoom and pan capabilities
- Hover tooltips with detailed information
- Customizable colors and labels
- Trend lines for correlation analysis

All functions return Plotly Figure objects that can be rendered in Streamlit or other frameworks.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Optional


def create_time_series_chart(
    df: pd.DataFrame,
    value_column: str,
    title: str,
    y_axis_label: str,
    color: str = 'blue'
) -> go.Figure:
    """
    Create a Plotly line chart for time series data.
    
    Args:
        df: DataFrame with datetime index and value column
        value_column: Name of the column containing values to plot
        title: Chart title
        y_axis_label: Label for the y-axis
        color: Color for the line (default: 'blue')
    
    Returns:
        Plotly Figure object with interactive time series chart
    """
    # Create the figure
    fig = go.Figure()
    
    # Add the time series trace
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[value_column],
        mode='lines',
        name=y_axis_label,
        line=dict(color=color, width=2),
        hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                      f'<b>{y_axis_label}</b>: %{{y:.2f}}<br>' +
                      '<extra></extra>'
    ))
    
    # Update layout with labels and interactive features
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=y_axis_label,
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        )
    )
    
    # Enable zoom and pan
    fig.update_xaxes(rangeslider_visible=False)
    
    return fig


def create_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    x_axis_label: str,
    y_axis_label: str,
    show_trendline: bool = True
) -> go.Figure:
    """
    Create a Plotly scatter plot for correlation visualization.
    
    Args:
        df: DataFrame with x and y columns
        x_column: Name of the column for x-axis values
        y_column: Name of the column for y-axis values
        title: Chart title
        x_axis_label: Label for the x-axis
        y_axis_label: Label for the y-axis
        show_trendline: Whether to show a trend line (default: True)
    
    Returns:
        Plotly Figure object with interactive scatter plot
    """
    # Create the figure
    fig = go.Figure()
    
    # Add scatter plot trace
    fig.add_trace(go.Scatter(
        x=df[x_column],
        y=df[y_column],
        mode='markers',
        name='Data Points',
        marker=dict(
            size=8,
            color='rgba(50, 100, 200, 0.6)',
            line=dict(width=1, color='rgba(50, 100, 200, 1)')
        ),
        hovertemplate='<b>' + x_axis_label + '</b>: %{x:.2f}<br>' +
                      '<b>' + y_axis_label + '</b>: %{y:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add trend line if requested
    if show_trendline and len(df) > 1:
        # Calculate linear regression
        x_values = df[x_column].values
        y_values = df[y_column].values
        
        # Use numpy for linear regression
        import numpy as np
        
        try:
            # Check if there's enough variance to compute a trendline
            if np.std(x_values) > 0 and np.std(y_values) > 0:
                z = np.polyfit(x_values, y_values, 1)
                p = np.poly1d(z)
                
                # Create trend line points
                x_trend = np.linspace(x_values.min(), x_values.max(), 100)
                y_trend = p(x_trend)
                
                fig.add_trace(go.Scatter(
                    x=x_trend,
                    y=y_trend,
                    mode='lines',
                    name='Trend Line',
                    line=dict(color='red', width=2, dash='dash'),
                    hovertemplate='<b>Trend Line</b><br>' +
                                  '<extra></extra>'
                ))
        except (np.linalg.LinAlgError, ValueError):
            # If trendline calculation fails (e.g., all values are constant),
            # skip adding the trendline
            pass
    
    # Update layout with labels and interactive features
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_label,
        yaxis_title=y_axis_label,
        hovermode='closest',
        template='plotly_white',
        showlegend=True,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        )
    )
    
    return fig
