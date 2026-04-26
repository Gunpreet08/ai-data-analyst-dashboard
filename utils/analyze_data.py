def get_shape(df):
    """
    Return number of rows and columns.
    """
    return df.shape


def get_columns(df):
    """
    Return list of column names.
    """
    return df.columns.tolist()


def get_dtypes(df):
    """
    Return data types of all columns.
    """
    return df.dtypes


def get_missing_values(df):
    """
    Return count of missing values per column.
    """
    return df.isnull().sum()


def get_numeric_summary(df):
    """
    Return summary statistics for numeric columns only.
    """
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return None
    return numeric_df.describe()


def get_numeric_columns(df):
    """
    Return list of numeric columns.
    """
    return df.select_dtypes(include=["number"]).columns.tolist()