import pandas as pd

def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns basic summary statistics for numeric columns of a DataFrame.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        pd.DataFrame: summary stats (count, mean, std, min, 25%, 50%, 75%, max)
    """
    return df.describe()
