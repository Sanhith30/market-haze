# Design Document: Market Haze

## Overview

Market Haze is a Streamlit-based dashboard application that visualizes and analyzes the relationship between Mumbai's Air Quality Index (AQI) and the Nifty 50 stock market index. The application follows a modular architecture with clear separation between data acquisition, data processing, and presentation layers.

The system fetches historical data from two external sources:
- Open-Meteo API for Mumbai AQI data
- Yahoo Finance (via yfinance) for Nifty 50 index data

After retrieving and aligning the data, the application computes correlation metrics and presents interactive visualizations using Plotly within a Streamlit interface.

## Architecture

The application follows a three-layer architecture:

1. **Data Layer**: Responsible for fetching raw data from external APIs
2. **Processing Layer**: Handles data cleaning, alignment, and statistical computations
3. **Presentation Layer**: Streamlit UI that orchestrates data flow and renders visualizations

```
┌─────────────────────────────────────────┐
│         Streamlit Dashboard UI          │
│         (Presentation Layer)            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        Data Processing Module           │
│  - Alignment, Cleaning, Correlation     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│          Data Loader Module             │
│  - AQI Fetcher  │  - Nifty 50 Fetcher   │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         External APIs                   │
│  - Open-Meteo   │  - Yahoo Finance      │
└─────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Data Loader Module (`data_loader.py`)

**Purpose**: Fetch historical data from external APIs and return pandas DataFrames.

**Functions**:

```python
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
    pass

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
    pass
```

**Implementation Details**:
- Use `openmeteo_requests` library with Mumbai coordinates (19.0760° N, 72.8777° E)
- Use `yfinance` with ticker symbol `^NSEI` for Nifty 50
- Return DataFrames with datetime index for easy alignment
- Handle API rate limits and connection errors gracefully

### 2. Data Processing Module (`data_processor.py`)

**Purpose**: Clean, align, and analyze data from multiple sources.

**Functions**:

```python
def align_datasets(aqi_df: pd.DataFrame, nifty_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align two datasets to common dates.
    
    Args:
        aqi_df: DataFrame with AQI data
        nifty_df: DataFrame with Nifty 50 data
    
    Returns:
        Tuple of (aligned_aqi_df, aligned_nifty_df) with matching date indices
    """
    pass

def compute_correlation(aqi_values: pd.Series, nifty_values: pd.Series) -> float:
    """
    Compute Pearson correlation coefficient between two series.
    
    Args:
        aqi_values: Series of AQI values
        nifty_values: Series of Nifty 50 values
    
    Returns:
        Pearson correlation coefficient (float between -1 and 1)
    """
    pass

def handle_missing_values(df: pd.DataFrame, method: str = 'forward_fill') -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: DataFrame with potential missing values
        method: Method to handle missing values ('forward_fill', 'drop', 'interpolate')
    
    Returns:
        DataFrame with missing values handled
    """
    pass
```

### 3. Dashboard UI (`app.py`)

**Purpose**: Main Streamlit application that orchestrates data flow and renders visualizations.

**Structure**:
- Page configuration and title
- Data loading section with error handling and loading indicators
- Visualization section with multiple charts
- Correlation analysis section

**Key Streamlit Components**:
- `st.title()`: Display dashboard title
- `st.spinner()`: Show loading indicators
- `st.error()`: Display error messages
- `st.metric()`: Display correlation coefficient
- `st.plotly_chart()`: Render interactive Plotly visualizations

## Data Models

### AQI DataFrame Schema
```
date: datetime64[ns] (index)
aqi: float64
```

### Nifty 50 DataFrame Schema
```
date: datetime64[ns] (index)
close: float64
```

### Aligned Dataset Schema
```
date: datetime64[ns] (index)
aqi: float64
nifty_close: float64
```

## Visualization Design

### 1. Time Series Chart - AQI
- **Type**: Line chart
- **X-axis**: Date (past 365 days)
- **Y-axis**: AQI value
- **Features**: Hover tooltips, zoom, pan
- **Color**: Orange/red gradient to indicate pollution levels

### 2. Time Series Chart - Nifty 50
- **Type**: Line chart
- **X-axis**: Date (past 365 days)
- **Y-axis**: Nifty 50 closing value
- **Features**: Hover tooltips, zoom, pan
- **Color**: Blue/green for market data

### 3. Scatter Plot - Correlation
- **Type**: Scatter plot
- **X-axis**: AQI value
- **Y-axis**: Nifty 50 closing value
- **Features**: Hover tooltips showing date, trend line
- **Purpose**: Visualize relationship between variables

### 4. Dual-Axis Time Series (Optional Enhancement)
- **Type**: Line chart with dual y-axes
- **Left Y-axis**: AQI
- **Right Y-axis**: Nifty 50
- **Purpose**: Show both metrics on same timeline for visual comparison

## Data Flow

1. User opens Streamlit dashboard
2. Dashboard displays loading indicator
3. Data Loader fetches AQI data from Open-Meteo API
4. Data Loader fetches Nifty 50 data from yfinance
5. Data Processor aligns datasets to common dates
6. Data Processor handles any missing values
7. Data Processor computes correlation coefficient
8. Dashboard renders time series visualizations
9. Dashboard renders scatter plot with correlation
10. Dashboard displays correlation metric
11. User interacts with visualizations (zoom, hover, pan)


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Date range completeness
*For any* data fetch request with a specified number of days, the returned DataFrame should contain data spanning approximately that number of days (within tolerance for weekends/holidays).
**Validates: Requirements 1.1, 2.1**

### Property 2: Missing value handling preservation
*For any* dataset with missing values, after applying the missing value handler, the resulting dataset should either have no missing values (if using forward fill or interpolation) or should have fewer rows (if using drop), and the non-missing values should remain unchanged.
**Validates: Requirements 1.3, 2.3**

### Property 3: Error messages on API failure
*For any* API request that fails, the system should return an error message that is non-empty and contains information about the failure type.
**Validates: Requirements 1.4, 2.4, 5.2**

### Property 4: Correlation computation correctness
*For any* two aligned numeric series, the computed Pearson correlation coefficient should match the result from pandas' built-in correlation function and should be a value between -1 and 1 inclusive.
**Validates: Requirements 3.1**

### Property 5: Dataset alignment consistency
*For any* two datasets with different date ranges, after alignment, both resulting datasets should have identical date indices and the same number of rows.
**Validates: Requirements 3.4**

### Property 6: Visualization data structure validity
*For any* dataset passed to a visualization function, the resulting Plotly figure should contain data traces with the same number of points as the input dataset.
**Validates: Requirements 1.2, 2.2, 3.3**

### Property 7: Chart configuration completeness
*For any* Plotly chart generated by the system, the figure should have non-empty axis labels, a non-empty title, and hover mode enabled.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 8: Error handling without crashes
*For any* processing error that occurs during data manipulation, the system should catch the exception, log it, and return a user-friendly error message without terminating the application.
**Validates: Requirements 5.3**

## Error Handling

The application implements a multi-layered error handling strategy:

### API Layer Errors
- **Connection Failures**: Catch network exceptions and return descriptive error messages
- **Rate Limiting**: Implement retry logic with exponential backoff
- **Invalid Responses**: Validate API response structure before processing
- **Timeout Errors**: Set reasonable timeout values and handle timeout exceptions

### Data Processing Errors
- **Missing Data**: Use configurable strategies (forward fill, interpolation, or drop)
- **Type Mismatches**: Validate data types before operations
- **Empty Datasets**: Check for empty DataFrames and handle gracefully
- **Alignment Failures**: Verify datasets have overlapping dates before alignment

### UI Layer Errors
- **Display Errors**: Wrap visualization code in try-except blocks
- **User Feedback**: Use Streamlit's error/warning components for user communication
- **Graceful Degradation**: Show partial results if some components fail

### Error Message Format
All error messages should follow this structure:
```
[Component]: [Error Type] - [Description]
Example: "Data Loader: API Error - Failed to fetch AQI data from Open-Meteo"
```

## Testing Strategy

The Market Haze application will use a dual testing approach combining unit tests and property-based tests to ensure correctness and robustness.

### Unit Testing

Unit tests will verify specific examples and integration points:

**Data Loader Tests**:
- Test successful API calls with known date ranges
- Test error handling for network failures
- Test data structure of returned DataFrames

**Data Processor Tests**:
- Test alignment with sample datasets of different sizes
- Test correlation computation with known input/output pairs
- Test missing value handling with specific examples

**Visualization Tests**:
- Test that chart generation produces valid Plotly figures
- Test that charts contain expected data traces

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using the **Hypothesis** library for Python.

**Configuration**:
- Each property-based test will run a minimum of 100 iterations
- Tests will use Hypothesis strategies to generate valid test data
- Each test will be tagged with a comment referencing the correctness property from this design document

**Property Test Requirements**:
- Each property-based test MUST be tagged with: `# Feature: market-haze, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Tests should use smart generators that constrain to valid input spaces

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: market-haze, Property 5: Dataset alignment consistency
@given(
    df1=st.dataframes(...),
    df2=st.dataframes(...)
)
def test_alignment_produces_matching_indices(df1, df2):
    aligned1, aligned2 = align_datasets(df1, df2)
    assert aligned1.index.equals(aligned2.index)
    assert len(aligned1) == len(aligned2)
```

**Property Tests to Implement**:
1. Date range completeness (Property 1)
2. Missing value handling preservation (Property 2)
3. Error messages on API failure (Property 3)
4. Correlation computation correctness (Property 4)
5. Dataset alignment consistency (Property 5)
6. Visualization data structure validity (Property 6)
7. Chart configuration completeness (Property 7)
8. Error handling without crashes (Property 8)

### Test Organization
- Unit tests: `tests/test_data_loader.py`, `tests/test_data_processor.py`, `tests/test_visualizations.py`
- Property tests: `tests/property_tests/test_properties.py`
- Test utilities: `tests/conftest.py` for shared fixtures and generators

### Testing Guidelines
- Write tests before or alongside implementation
- Focus on core functional logic and important edge cases
- Avoid over-mocking; test real functionality where possible
- Property tests should catch bugs that unit tests might miss
- Both test types are valuable and complement each other
