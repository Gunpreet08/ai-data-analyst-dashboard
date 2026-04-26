import pandas as pd


def load_csv(uploaded_file):
    """
    Load uploaded CSV file into a Pandas DataFrame.
    """
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)