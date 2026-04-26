import re


def render_kpi_value(df, kpi_name):
    kpi_lower = kpi_name.lower()

    # Conditional KPI: Example "Employees with Age > 25"
    match = re.search(r"(\w+)\s*>\s*(\d+)", kpi_lower)
    if match:
        condition_col = match.group(1)
        condition_value = int(match.group(2))

        for col in df.columns:
            if col.lower() == condition_col:
                return int((df[col] > condition_value).sum())

    # Match exact column name inside KPI text
    matched_col = None

    for col in df.columns:
        col_lower = col.lower()

        if col_lower in kpi_lower:
            matched_col = col
            break

    if matched_col is None:
        return "N/A"

    # Count / number
    if "number" in kpi_lower or "count" in kpi_lower:
        return int(df[matched_col].count())

    # Numeric KPI calculations
    if df[matched_col].dtype.kind in "iufc":
        if "average" in kpi_lower or "mean" in kpi_lower:
            return round(df[matched_col].mean(), 2)

        if "total" in kpi_lower or "sum" in kpi_lower:
            return round(df[matched_col].sum(), 2)

        if "max" in kpi_lower or "highest" in kpi_lower:
            return round(df[matched_col].max(), 2)

        if "min" in kpi_lower or "lowest" in kpi_lower:
            return round(df[matched_col].min(), 2)

        return round(df[matched_col].mean(), 2)

    return df[matched_col].nunique()

# import re
# def render_kpi_value(df, kpi_name):
#     """
#     Try to calculate a KPI value from a KPI name suggested by AI.
#     """
#     kpi_lower = kpi_name.lower()

#     # Handle condition like "Experience > 2"
#     match = re.search(r"(\w+)\s*>\s*(\d+)", kpi_lower)
#     if match:
#         col = match.group(1)
#         value = int(match.group(2))

#         for df_col in df.columns:
#             if df_col.lower() == col:
#                 return int((df[df_col] > value).sum())

#     for col in df.columns:
#         col_lower = col.lower()

#         if col_lower in kpi_lower:
#             # 🧠 NEW: Handle "number of", "count"
#             if "number" in kpi_lower or "count" in kpi_lower:
#                 return df[col].count()
            
#             if "average" in kpi_lower or "mean" in kpi_lower:
#                 if df[col].dtype.kind in "iufc":
#                     return round(df[col].mean(), 2)

#             if "max" in kpi_lower or "highest" in kpi_lower:
#                 if df[col].dtype.kind in "iufc":
#                     return round(df[col].max(), 2)

#             if "min" in kpi_lower or "lowest" in kpi_lower:
#                 if df[col].dtype.kind in "iufc":
#                     return round(df[col].min(), 2)

#             if "total" in kpi_lower or "sum" in kpi_lower:
#                 if df[col].dtype.kind in "iufc":
#                     return round(df[col].sum(), 2)
                
#             # If no operation mentioned → default to MEAN
            
#             return round(df[col].mean(), 2)

#             return df[col].nunique()

#     return "N/A"