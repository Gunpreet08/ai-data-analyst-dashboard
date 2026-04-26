def generate_basic_insights(df):
    """
    Generate business-style insights for numeric columns.
    """
    insights = []

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        insights.append("No numeric columns found for analysis.")
        return insights

    for col in numeric_cols:
        mean_val = df[col].mean()
        min_val = df[col].min()
        max_val = df[col].max()
        median_val = df[col].median()

        # Base insight
        insights.append(
            f"The {col} values range from {min_val:.2f} to {max_val:.2f}, with an average of {mean_val:.2f}."
        )

        # Variation analysis
        if mean_val != 0:
            variation_ratio = (max_val - min_val) / mean_val

            if variation_ratio > 1:
                insights.append(
                    f"{col} shows high variability, which may indicate significant differences across records."
                )
            elif variation_ratio > 0.5:
                insights.append(
                    f"{col} shows moderate variation, suggesting some level of diversity in the dataset."
                )
            else:
                insights.append(
                    f"{col} is relatively consistent, indicating similar values across most records."
                )

        # Median comparison insight
        if abs(mean_val - median_val) > 0.1 * mean_val:
            insights.append(
                f"The difference between mean and median suggests potential skewness in {col} distribution."
            )

    return insights


def generate_correlation_insight(df, x_col, y_col):
    correlation = df[x_col].corr(df[y_col])

    if correlation > 0.7:
        return (
            f"There is a strong positive relationship between {x_col} and {y_col}. "
            f"This suggests that as {x_col} increases, {y_col} also tends to increase significantly."
        )
    elif correlation > 0.3:
        return (
            f"There is a moderate positive relationship between {x_col} and {y_col}, "
            f"indicating some level of association between these variables."
        )
    elif correlation > -0.3:
        return (
            f"There is little to no clear relationship between {x_col} and {y_col}, "
            f"suggesting they may be independent."
        )
    elif correlation > -0.7:
        return (
            f"There is a moderate negative relationship between {x_col} and {y_col}, "
            f"meaning as one increases, the other tends to decrease."
        )
    else:
        return (
            f"There is a strong negative relationship between {x_col} and {y_col}, "
            f"indicating an inverse relationship between these variables."
        )