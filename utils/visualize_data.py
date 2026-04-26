import matplotlib.pyplot as plt


def plot_histogram(df, column):
    """
    Create histogram for a numeric column.
    """
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.hist(df[column].dropna(), bins=20)
    ax.set_title(f"Histogram of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    fig.tight_layout() 
    return fig


def plot_scatter(df, x_col, y_col):
    """
    Create scatter plot for two numeric columns.
    """
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(df[x_col], df[y_col])
    ax.set_title(f"{x_col} vs {y_col}")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    fig.tight_layout()
    return fig