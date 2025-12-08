"""
Market Haze - Streamlit Dashboard

A dashboard application that visualizes and analyzes the relationship between
Mumbai's Air Quality Index (AQI) and the Nifty 50 stock market index.
"""

import streamlit as st
import pandas as pd
from data_loader import fetch_mumbai_aqi, fetch_nifty50, APIError
from data_processor import align_datasets, compute_correlation, handle_missing_values
from visualizations import create_time_series_chart, create_scatter_plot


# Page configuration
st.set_page_config(
    page_title="Market Haze - AQI vs Nifty 50",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dashboard title and description
st.title("🌫️ Market Haze: Mumbai AQI vs Nifty 50 Analysis")
st.markdown("""
This dashboard explores the relationship between Mumbai's Air Quality Index (AQI) 
and the Nifty 50 stock market index over the past year. Discover potential correlations 
between air quality and market performance.
""")

st.divider()

# Data Loading Section
st.header("📊 Loading Data")

# Initialize variables for data
aqi_df = None
nifty_df = None
data_load_success = False

# Load AQI data
with st.spinner("Fetching Mumbai AQI data..."):
    try:
        aqi_df = fetch_mumbai_aqi(days=365)
        st.success(f"✅ Successfully loaded {len(aqi_df)} days of AQI data")
    except APIError as e:
        st.error(f"❌ Failed to load AQI data: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error loading AQI data: {str(e)}")

# Load Nifty 50 data
with st.spinner("Fetching Nifty 50 data..."):
    try:
        nifty_df = fetch_nifty50(days=365)
        st.success(f"✅ Successfully loaded {len(nifty_df)} days of Nifty 50 data")
    except APIError as e:
        st.error(f"❌ Failed to load Nifty 50 data: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error loading Nifty 50 data: {str(e)}")

# Check if both datasets loaded successfully
if aqi_df is not None and nifty_df is not None:
    data_load_success = True
else:
    st.warning("⚠️ Cannot proceed with analysis. Please check the error messages above.")
    st.stop()

st.divider()

# Data Processing Section
st.header("🔄 Processing Data")

try:
    with st.spinner("Processing and aligning datasets..."):
        # Handle missing values in both datasets
        aqi_df = handle_missing_values(aqi_df, method='forward_fill')
        nifty_df = handle_missing_values(nifty_df, method='forward_fill')
        
        # Align datasets to common dates
        aligned_aqi, aligned_nifty = align_datasets(aqi_df, nifty_df)
        
        # Check if we have data after alignment
        if len(aligned_aqi) == 0 or len(aligned_nifty) == 0:
            st.error("❌ No overlapping dates found between AQI and Nifty 50 datasets.")
            st.stop()
        
        st.success(f"✅ Successfully aligned datasets: {len(aligned_aqi)} common dates")
        
        # Compute correlation coefficient
        correlation = compute_correlation(aligned_aqi['aqi'], aligned_nifty['close'])
        
        st.success(f"✅ Correlation computed successfully")
        
except Exception as e:
    st.error(f"❌ Error during data processing: {str(e)}")
    st.warning("⚠️ Cannot proceed with visualization. Please check the error above.")
    st.stop()

st.divider()

# Visualization Section
st.header("📈 Analysis Results")

# Display correlation coefficient
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.metric(
        label="Pearson Correlation Coefficient",
        value=f"{correlation:.4f}",
        help="Correlation between Mumbai AQI and Nifty 50. Values range from -1 (perfect negative) to +1 (perfect positive)."
    )

st.divider()

# Create two columns for time series charts
st.subheader("📊 Time Series Analysis")
col_left, col_right = st.columns(2)

with col_left:
    # AQI Time Series Chart
    try:
        aqi_chart = create_time_series_chart(
            df=aligned_aqi,
            value_column='aqi',
            title='Mumbai Air Quality Index (AQI)',
            y_axis_label='AQI Value',
            color='orange'
        )
        st.plotly_chart(aqi_chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating AQI chart: {str(e)}")

with col_right:
    # Nifty 50 Time Series Chart
    try:
        nifty_chart = create_time_series_chart(
            df=aligned_nifty,
            value_column='close',
            title='Nifty 50 Index',
            y_axis_label='Closing Value',
            color='blue'
        )
        st.plotly_chart(nifty_chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating Nifty 50 chart: {str(e)}")

st.divider()

# Correlation Scatter Plot
st.subheader("🔍 Correlation Analysis")
try:
    # Combine data for scatter plot
    scatter_df = pd.DataFrame({
        'aqi': aligned_aqi['aqi'],
        'nifty_close': aligned_nifty['close']
    })
    
    scatter_chart = create_scatter_plot(
        df=scatter_df,
        x_column='aqi',
        y_column='nifty_close',
        title='AQI vs Nifty 50: Correlation Scatter Plot',
        x_axis_label='Air Quality Index (AQI)',
        y_axis_label='Nifty 50 Closing Value',
        show_trendline=True
    )
    st.plotly_chart(scatter_chart, use_container_width=True)
except Exception as e:
    st.error(f"Error creating scatter plot: {str(e)}")

# Footer with interpretation guide
st.divider()
st.markdown("""
### 📖 Interpretation Guide
- **Correlation Coefficient**: 
  - Close to +1: Strong positive correlation (AQI and Nifty 50 move together)
  - Close to -1: Strong negative correlation (AQI and Nifty 50 move in opposite directions)
  - Close to 0: Little to no linear relationship
- **Interactive Charts**: Hover over data points for details, zoom in/out, and pan to explore specific time periods
""")
