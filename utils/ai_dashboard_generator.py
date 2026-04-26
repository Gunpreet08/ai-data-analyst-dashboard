import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def generate_dashboard_plan(df):
    """
    Generate AI-based dashboard recommendations from dataset metadata.
    Returns:
        plan_dict, error_message
    """
    try:
        column_info = []
        for col in df.columns:
            column_info.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "sample_values": df[col].dropna().astype(str).head(3).tolist()
            })

        prompt = f"""
You are an expert data analyst and dashboard designer.

Based on the dataset metadata below, create a dashboard recommendation plan.

Return only valid JSON in this exact format:

{{
  "dashboard_title": "string",
  "kpis": ["kpi1", "kpi2", "kpi3"],
  "sections": [
    {{
      "section_title": "string",
      "purpose": "string"
    }}
  ],
  "charts": [
    {{
      "chart_type": "histogram/bar/scatter",
      "title": "string",
      "x": "column_name_or_null",
      "y": "column_name_or_null",
      "reason": "string"
    }}
  ]
}}

Rules:
- Recommend 2 to 4 KPIs
- Recommend 2 to 4 charts only
- Do not recommend line charts.
- Use ONLY columns that exist in the dataset metadata.
- Prefer meaningful chart choices based on column types
- If a chart does not need y, set y to null
- If a chart does not need x, set x to null
- Do not include any explanation outside JSON
- Never invent column names such as Role, Department, Category, etc.
- For histogram, x must be an existing numeric column and y must be null.
- For scatter, both x and y must be existing numeric columns.
- For bar chart, x must be an existing categorical column and y must be an existing numeric column. If no categorical column exists, avoid bar charts.
- If no valid chart can be created, do not include it.
- For numeric distribution charts, prefer histogram over bar.
- Use bar charts mainly for categorical columns or grouped comparisons.
- Do not create bar charts with high-cardinality numeric columns unless grouped by another column.
- Do not return raw column names as KPIs.
- If multiple numeric columns exist, vary histogram across different columns instead of always choosing the same one.
- Always include a clear aggregation or meaning.

Examples:
BAD → "Age", "Salary", "Experience"
GOOD → "Average Age", "Total Salary", "Max Salary", "Employees with Experience > 2"

- For numeric columns, prefer:
  average, sum, min, max, count-based conditions

- KPI names must be meaningful and self-explanatory.
- Do not use words like "Category", "Categories", "Group", or "Type" in chart titles unless such a column actually exists.
- Do not create bar charts for numeric columns alone. Example: "Salary Count" is not useful.
- If x is numeric and y is null, use histogram, not bar.
- If both x and y are numeric, use scatter.
- If using bar chart, x should preferably be categorical and y should be numeric.
- If the dataset has very few rows, prefer simple charts: histogram and scatter.
- Do not recommend line charts unless there is a datetime/date column.
Dataset Metadata:
{json.dumps(column_info, indent=2)}
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        data = response.json()
        raw_text = data.get("response", "").strip()

        # Try parsing response as JSON
        plan = json.loads(raw_text)

        return plan, None

    except Exception as e:
        return None, str(e)