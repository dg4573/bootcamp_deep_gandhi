import pandas as pd
import numpy as np

def detect_outliers_iqr(series):
    """
    Detect outliers using the Interquartile Range (IQR) rule.
    Returns a boolean Series where True = outlier.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (series < lower) | (series > upper)

def detect_outliers_zscore(series, threshold = 3.0):
    """
    Detect outliers using Z-score method.
    Returns a boolean Series where True = outlier.
    """
    mean = series.mean()
    std = series.std()
    zscores = (series - mean) / std
    return np.abs(zscores) > threshold

def winsorize_series(series, lower = 0.05, upper = 0.95):
    """
    Winsorize a Series by capping values at the given lower/upper quantiles.
    Stretch goal: use for reducing extreme outliers.
    """
    lower_bound = series.quantile(lower)
    upper_bound = series.quantile(upper)
    return series.clip(lower=lower_bound, upper=upper_bound)