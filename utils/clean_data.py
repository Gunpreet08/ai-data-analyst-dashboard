def remove_duplicates(df):
    """
    Remove duplicate rows from dataset.
    """
    before = df.shape[0]
    df = df.drop_duplicates().copy()
    after = df.shape[0]
    return df, before - after


import pandas as pd


def fill_missing_values(df):
    """
    Fill missing values:
    - numeric columns -> mean
    - categorical columns -> mode
    """
    df = df.copy()

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
        else:
            mode_value = df[col].mode()
            if not mode_value.empty:
                df[col] = df[col].fillna(mode_value[0])

    return df