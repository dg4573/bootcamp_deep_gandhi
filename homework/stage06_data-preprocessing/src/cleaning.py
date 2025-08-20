import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def fill_missing_median(df, numeric_cols):
    """
    Fill missing values in numeric columns with median
    """
    df = df.copy()
    for col in numeric_cols:
        if col in df.columns:
            df[col].fillna(df[col].median(), inplace=True)
    return df

def drop_missing(df, cols=None):
    """
    Drop rows with missing values
    """
    df = df.copy()
    return df.dropna(subset=cols)

def normalize_data(df, numeric_cols):
    """
    Normalize numeric columns to 0-1 using MinMax scaling
    """
    df = df.copy()
    scaler = MinMaxScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df
