SUPPORTED_ACTIONS = {
    "drop_column",
    "convert_dtype",
    "filter_rows",
    "fill_missing",
    "rename_column",
}

SUPPORTED_DTYPES = {"string", "int", "float", "datetime"}
SUPPORTED_OPERATORS = {">", "<", ">=", "<=", "==", "!="}
SUPPORTED_STRATEGIES = {"mean", "median", "mode", "zero"}

def resolve_column_name(name, df_columns):
    """
    Match a column name case-insensitively.
    Returns the exact dataframe column name if found, else None.
    """
    if not name:
        return None

    lookup = {col.lower(): col for col in df_columns}
    return lookup.get(str(name).strip().lower())

def validate_prep_plan(plan, df):
    """
    Validate AI-generated preparation plan.
    Returns: (valid_actions, invalid_actions)
    """
    valid_actions = []
    invalid_actions = []

    if not plan or "actions" not in plan:
        return valid_actions, [{"reason": "Plan is empty or missing 'actions' key."}]

    df_columns = list(df.columns)

    for action in plan["actions"]:
        action_type = str(action.get("type", "")).strip().lower()

        if action_type not in SUPPORTED_ACTIONS:
            invalid_actions.append({
                "action": action,
                "reason": f"Unsupported action type: {action_type}"
            })
            continue

        if action_type == "drop_column":
            raw_columns = action.get("columns", [])
            resolved_columns = [resolve_column_name(col, df_columns) for col in raw_columns]

            if raw_columns and all(col is not None for col in resolved_columns):
                valid_actions.append({
                    "type": "drop_column",
                    "columns": resolved_columns
                })
            else:
                invalid_actions.append({
                    "action": action,
                    "reason": "One or more columns do not exist for drop_column."
                })

        elif action_type == "convert_dtype":
            column = resolve_column_name(action.get("column"), df_columns)
            target_type = str(action.get("target_type", "")).strip().lower()

            if column and target_type in SUPPORTED_DTYPES:
                valid_actions.append({
                    "type": "convert_dtype",
                    "column": column,
                    "target_type": target_type
                })
            else:
                invalid_actions.append({
                    "action": action,
                    "reason": "Invalid column or target_type for convert_dtype."
                })

        elif action_type == "filter_rows":
            column = resolve_column_name(action.get("column"), df_columns)
            operator = str(action.get("operator", "")).strip()
            value = action.get("value")

            if column and operator in SUPPORTED_OPERATORS:
                valid_actions.append({
                    "type": "filter_rows",
                    "column": column,
                    "operator": operator,
                    "value": value
                })
            else:
                invalid_actions.append({
                    "action": action,
                    "reason": "Invalid column or operator for filter_rows."
                })

        elif action_type == "fill_missing":
            column = resolve_column_name(action.get("column"), df_columns)
            strategy = str(action.get("strategy", "")).strip().lower()

            if column and strategy in SUPPORTED_STRATEGIES:
                valid_actions.append({
                    "type": "fill_missing",
                    "column": column,
                    "strategy": strategy
                })
            else:
                invalid_actions.append({
                    "action": action,
                    "reason": "Invalid column or strategy for fill_missing."
                })

        elif action_type == "rename_column":
            old_name = resolve_column_name(action.get("old_name"), df_columns)
            new_name = str(action.get("new_name", "")).strip()

            if old_name and new_name:
                valid_actions.append({
                    "type": "rename_column",
                    "old_name": old_name,
                    "new_name": new_name
                })
            else:
                invalid_actions.append({
                    "action": action,
                    "reason": "Invalid old_name or new_name for rename_column."
                })

    return valid_actions, invalid_actions