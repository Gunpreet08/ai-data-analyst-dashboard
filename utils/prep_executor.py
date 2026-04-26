import pandas as pd


def execute_prep_plan(df, actions):
    """
    Execute validated preparation actions on the dataframe.
    Returns: (updated_df, execution_log)
    """
    updated_df = df.copy()
    execution_log = []

    for action in actions:
        action_type = action.get("type")

        try:
            if action_type == "drop_column":
                columns = action.get("columns", [])
                existing_columns = [col for col in columns if col in updated_df.columns]

                if not existing_columns:
                    execution_log.append("No matching columns found to drop — no change needed")
                    continue

                updated_df = updated_df.drop(columns=existing_columns)
                execution_log.append(f"Dropped columns: {existing_columns}")

            elif action_type == "convert_dtype":
                column = action.get("column")
                target_type = action.get("target_type")

                if column not in updated_df.columns:
                    execution_log.append(f"Skipped {column}: column not found")
                    continue

                current_dtype = str(updated_df[column].dtype)                

                if target_type == "float":
                    if "float" in current_dtype:
                        execution_log.append(f"{column} is already in float format — no change needed")
                        continue
                    updated_df[column] = pd.to_numeric(updated_df[column], errors="coerce").astype(float)
                    execution_log.append(f"Converted {column} to float")

                elif target_type == "int":
                    if "int" in current_dtype:
                        execution_log.append(f"{column} is already in integer format — no change needed")
                        continue
                    updated_df[column] = pd.to_numeric(updated_df[column], errors="coerce").astype("Int64")
                    execution_log.append(f"Converted {column} to int")

                elif target_type == "string":
                    if current_dtype == "object":
                        execution_log.append(f"{column} is already in string format — no change needed")
                        continue
                    updated_df[column] = updated_df[column].astype(str)
                    execution_log.append(f"Converted {column} to string")

                elif target_type == "datetime":
                    if "datetime" in current_dtype:
                        execution_log.append(f"{column} is already in datetime format — no change needed")
                        continue
                    updated_df[column] = pd.to_datetime(updated_df[column], errors="coerce")
                    execution_log.append(f"Converted {column} to datetime")

                # execution_log.append(f"Converted {column} to {target_type}")

            elif action_type == "filter_rows":
                column = action.get("column")
                operator = action.get("operator")
                value = action.get("value")

                if column not in updated_df.columns:
                    execution_log.append(f"Skipped filter: {column} not found")
                    continue

                numeric_col = pd.to_numeric(updated_df[column], errors="coerce")

                if operator == ">":
                    updated_df = updated_df[numeric_col > float(value)]
                elif operator == "<":
                    updated_df = updated_df[numeric_col < float(value)]
                elif operator == ">=":
                    updated_df = updated_df[numeric_col >= float(value)]
                elif operator == "<=":
                    updated_df = updated_df[numeric_col <= float(value)]
                elif operator == "==":
                    updated_df = updated_df[updated_df[column].astype(str) == str(value)]
                elif operator == "!=":
                    updated_df = updated_df[updated_df[column].astype(str) != str(value)]

                execution_log.append(f"Filtered rows where {column} {operator} {value}")

            elif action_type == "fill_missing":
                column = action.get("column")
                strategy = action.get("strategy")

                if column not in updated_df.columns:
                    execution_log.append(f"Skipped fill_missing: {column} not found")
                    continue

                if strategy == "mean":
                    updated_df[column] = updated_df[column].fillna(updated_df[column].mean())
                elif strategy == "median":
                    updated_df[column] = updated_df[column].fillna(updated_df[column].median())
                elif strategy == "mode":
                    mode_value = updated_df[column].mode()
                    if not mode_value.empty:
                        updated_df[column] = updated_df[column].fillna(mode_value[0])
                elif strategy == "zero":
                    updated_df[column] = updated_df[column].fillna(0)

                execution_log.append(f"Filled missing values in {column} using {strategy}")

            elif action_type == "rename_column":
                old_name = action.get("old_name")
                new_name = action.get("new_name")
                if old_name not in updated_df.columns:
                    execution_log.append(f"Skipped rename: {old_name} not found")
                    continue

                if old_name == new_name:
                    execution_log.append(f"{old_name} already has the requested name — no change needed")
                    continue
                updated_df = updated_df.rename(columns={old_name: new_name})
                execution_log.append(f"Renamed column {old_name} to {new_name}")

        except Exception as e:
            execution_log.append(f"Failed to execute {action_type}: {str(e)}")

    return updated_df, execution_log