# Building Market Haze: A Real-Time AQI-Market Correlation Dashboard with Kiro AI

## Introduction

In this blog post, I'll share my experience building **Market Haze**, a Streamlit dashboard that analyzes the correlation between Mumbai's Air Quality Index (AQI) and the Nifty 50 stock market index, using Kiro AI to accelerate development.

## The Problem

Understanding the relationship between environmental factors and market performance is crucial for investors and policymakers. However, building a data analytics dashboard that:
- Fetches data from multiple APIs
- Handles missing values and alignment issues
- Provides interactive visualizations
- Ensures correctness through comprehensive testing

...can be time-consuming and error-prone.

## The Solution: Market Haze

Market Haze is a Python-based dashboard that:
- Fetches historical AQI data from Open-Meteo API
- Retrieves Nifty 50 index data from Yahoo Finance
- Aligns datasets to common dates
- Computes correlation coefficients
- Displays interactive visualizations using Plotly

### Architecture

The application follows a three-layer architecture:

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
```

## How Kiro Accelerated Development

### 1. Spec-Driven Development Workflow

Kiro guided me through a structured workflow:

**Requirements Phase**: Using EARS (Easy Approach to Requirements Syntax), Kiro helped me formalize requirements:

```markdown
### Requirement 1
**User Story:** As a data analyst, I want to view historical AQI data 
for Mumbai over the past year, so that I can understand air quality trends.

#### Acceptance Criteria
1. WHEN the Dashboard starts, THE Data Loader SHALL fetch Mumbai AQI 
   data for the past 365 days from the Open-Meteo API
2. WHEN AQI data is retrieved, THE Dashboard SHALL display the data 
   in a time series visualization
```

**Design Phase**: Kiro generated a comprehensive design document including:
- Component interfaces
- Data models
- **8 Correctness Properties** for property-based testing
- Error handling strategy

**Implementation Phase**: Kiro broke down the design into 20+ actionable tasks with clear dependencies.

### 2. Property-Based Testing Integration

One of Kiro's most powerful features is its focus on correctness through property-based testing. Here's an example:

**Correctness Property 5: Dataset alignment consistency**
```python
# Feature: market-haze, Property 5: Dataset alignment consistency
@given(
    df1=dataframes_with_dates(),
    df2=dataframes_with_dates()
)
def test_dataset_alignment_consistency(df1, df2):
    """For any two datasets, after alignment, both should have 
    identical date indices and the same number of rows."""
    aligned1, aligned2 = align_datasets(df1, df2)
    
    # Both should have same indices
    assert aligned1.index.equals(aligned2.index)
    
    # Both should have same length
    assert len(aligned1) == len(aligned2)
```

This property runs 100+ iterations with randomly generated data, catching edge cases that manual testing would miss.

### 3. Code Generation and Debugging

Kiro generated production-ready code with:
- Comprehensive docstrings
- Error handling
- Type hints
- Inline comments

**Example: Data Alignment Function**
```python
def align_datasets(aqi_df: pd.DataFrame, nifty_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align two datasets to common dates.
    
    This function ensures both datasets have the same date indices by performing
    an inner join. This is necessary because:
    - AQI data is available every day
    - Nifty 50 data is only available on trading days (excludes weekends/holidays)
    """
    aligned_aqi = aqi_df.join(nifty_df, how='inner', rsuffix='_nifty')
    aligned_nifty = nifty_df.join(aqi_df, how='inner', rsuffix='_aqi')
    
    # Keep only the original columns
    aligned_aqi = aligned_aqi[[col for col in aligned_aqi.columns if not col.endswith('_nifty')]]
    aligned_nifty = aligned_nifty[[col for col in aligned_nifty.columns if not col.endswith('_aqi')]]
    
    return aligned_aqi, aligned_nifty
```

### 4. Real-Time Problem Solving

When I encountered a timezone mismatch issue preventing data alignment, Kiro:
1. Identified the root cause (UTC vs timezone-naive indices)
2. Proposed a fix
3. Implemented the solution
4. Verified with tests

**The Fix:**
```python
# Convert timezone-aware index to timezone-naive for compatibility
df.index = df.index.tz_localize(None)
```

## Results & Impact

### Development Metrics
- **Total Tests**: 63 (9 property-based, 54 unit tests)
- **Test Coverage**: All 8 correctness properties validated
- **Lines of Code**: 800+ lines of production code
- **Development Time**: Significantly reduced compared to manual development

### Test Results
```
========================== test session starts ==========================
collected 63 items

tests/property_tests/test_properties.py ........... [100%]
tests/test_data_loader.py ...................... [100%]
tests/test_data_processor.py ...................... [100%]
tests/test_visualizations.py .................... [100%]

========================== 63 passed in 19.34s ==========================
```

### Dashboard Features
✅ Real-time data fetching from two APIs
✅ Automatic data alignment and cleaning
✅ Interactive Plotly visualizations
✅ Correlation analysis with statistical validation
✅ Comprehensive error handling

## Key Takeaways

### What Worked Well
1. **Spec-Driven Development**: Having formal requirements and design documents ensured clarity
2. **Property-Based Testing**: Caught edge cases that would have been missed
3. **Iterative Workflow**: Requirements → Design → Tasks → Implementation
4. **AI Assistance**: Kiro handled boilerplate code, allowing focus on business logic

### Lessons Learned
1. **Timezone Handling**: Always normalize datetime indices when combining data sources
2. **API Rate Limits**: Implement caching to avoid hitting API limits
3. **Testing Strategy**: Combine unit tests (specific cases) with property tests (general behavior)

## Conclusion

Building Market Haze with Kiro demonstrated how AI-assisted development can:
- Accelerate development without sacrificing quality
- Ensure correctness through property-based testing
- Provide structure through spec-driven workflows
- Handle debugging and problem-solving in real-time

The result is a production-ready dashboard with comprehensive test coverage, built in a fraction of the time traditional development would require.

## Try It Yourself

**GitHub Repository**:https://github.com/Sanhith30/market-haze.git

**Installation:**
```bash
git clone (https://github.com/Sanhith30/market-haze.git)
cd market-haze
pip install -r requirements.txt
streamlit run app.py
```

## Screenshots



---

**Built with**: Python, Streamlit, Plotly, Pandas, Hypothesis, and Kiro AI

**Tags**: #AI #DataScience #Streamlit #PropertyBasedTesting #KiroAI #Python
