import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

# Import your functions
from app.main import service_efficiency, find_savings, detect_anomalies, service_trends, forecast_service

# Sample test data
@pytest.fixture
def sample_df():
    data = {
        "Date": pd.date_range("2025-01-01", periods=5, freq="D"),
        "Cost": [10, 20, 15, 25, 30],
        "Service": ["EC2", "EC2", "S3", "S3", "Lambda"]
    }
    return pd.DataFrame(data)

# ============================
# Test service_efficiency
# ============================
def test_service_efficiency(sample_df):
    df_eff = service_efficiency(sample_df)
    assert "Service" in df_eff.columns
    assert "Total Spend" in df_eff.columns
    assert all(df_eff["Efficiency (%)"] >= 0) and all(df_eff["Efficiency (%)"] <= 100)
    assert len(df_eff) == sample_df["Service"].nunique()

# ============================
# Test find_savings
# ============================
def test_find_savings(sample_df):
    savings_df = find_savings(sample_df)
    # Should return a DataFrame with expected columns
    expected_cols = ["Recommendation", "Potential Saving", "Effort", "ROI"]
    assert all(col in savings_df.columns for col in expected_cols)

# ============================
# Test detect_anomalies
# ============================
def test_detect_anomalies(sample_df):
    anomalies_df = detect_anomalies(sample_df)
    # Should be a DataFrame (can be empty)
    assert isinstance(anomalies_df, pd.DataFrame)
    if not anomalies_df.empty:
        assert "Reason" in anomalies_df.columns
        assert "Service" in anomalies_df.columns

# ============================
# Test service_trends
# ============================
def test_service_trends(sample_df):
    trends_df, season_df = service_trends(sample_df)
    assert isinstance(trends_df, pd.DataFrame)
    assert isinstance(season_df, pd.DataFrame)
    if not trends_df.empty:
        assert "Trend" in trends_df.columns
    if not season_df.empty:
        assert "Max Weekly Avg" in season_df.columns

# ============================
# Test forecast_service
# ============================
def test_forecast_service(sample_df):
    forecast_df = forecast_service(sample_df, days=3)
    assert isinstance(forecast_df, pd.DataFrame)
    if not forecast_df.empty:
        assert all(col in forecast_df.columns for col in ["Service", "Date", "Forecast"])
        # Forecast should have more dates than original
        assert forecast_df["Date"].max() > sample_df["Date"].max()
