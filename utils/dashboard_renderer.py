import matplotlib.pyplot as plt


def clean_value(value):
    if value in [None, "None", "none", "null", ""]:
        return None
    return value


def render_chart(df, chart_config):
    chart_type = str(chart_config.get("chart_type", "")).lower()
    x = clean_value(chart_config.get("x"))
    y = clean_value(chart_config.get("y"))

    fig, ax = plt.subplots(figsize=(5, 3))

    try:
        if chart_type == "histogram":
            col = x or y

            if col not in df.columns:
                return None

            ax.hist(df[col].dropna(), bins=20)
            ax.set_title(f"{col} Distribution")
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")

        elif chart_type == "scatter":
            if x not in df.columns or y not in df.columns:
                return None

            ax.scatter(df[x], df[y])
            ax.set_title(f"{x} vs {y}")
            ax.set_xlabel(x)
            ax.set_ylabel(y)

        elif chart_type == "bar":
            if x in df.columns and y in df.columns:
                grouped = df.groupby(x)[y].mean()
                grouped.plot(kind="bar", ax=ax)
                ax.set_title(f"Average {y} by {x}")
                ax.set_xlabel(x)
                ax.set_ylabel(f"Average {y}")

            elif x in df.columns:
                df[x].value_counts().plot(kind="bar", ax=ax)
                ax.set_title(f"{x} Count")
                ax.set_xlabel(x)
                ax.set_ylabel("Count")

            elif y in df.columns:
                df[y].value_counts().plot(kind="bar", ax=ax)
                ax.set_title(f"{y} Count")
                ax.set_xlabel(y)
                ax.set_ylabel("Count")

            else:
                return None

        else:
            return None

        fig.tight_layout()
        return fig

    except Exception:
        return None