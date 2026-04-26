# import requests
import json

# OLLAMA_URL = "http://localhost:11434/api/generate"
# MODEL_NAME = "llama3.2"
from utils.groq_client import get_groq_response

def extract_json(text):
    """
    Extract JSON object from model output, even if extra text is present.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in AI response.")
    return text[start:end + 1]


def generate_prep_plan(df, user_request):
    """
    Generate a structured data preparation plan from user request.
    Returns: (plan_dict, error_message)
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
You are a data preparation assistant.

Convert the user's request into a valid JSON action plan.

Allowed action types:
1. drop_column
2. convert_dtype
3. filter_rows
4. fill_missing
5. rename_column

Return only valid JSON in this exact format:

{{
  "actions": [
    {{
      "type": "drop_column",
      "columns": ["column1", "column2"]
    }},
    {{
      "type": "convert_dtype",
      "column": "column_name",
      "target_type": "string/int/float/datetime"
    }},
    {{
      "type": "filter_rows",
      "column": "column_name",
      "operator": ">/</>=/<=/==/!=",
      "value": "some_value"
    }},
    {{
      "type": "fill_missing",
      "column": "column_name",
      "strategy": "mean/median/mode/zero"
    }},
    {{
      "type": "rename_column",
      "old_name": "old_column",
      "new_name": "new_column"
    }}
  ]
}}

Rules:
- Use only columns from the dataset metadata.
- Do not include any explanation outside JSON.
- If the request contains an unsupported operation, do not guess.
- Do not map unsupported requests to the nearest supported action.
- Only return an action if it clearly matches one of the allowed action types.
- If nothing supported can be extracted, return:
  {{"actions": []}}
- Do not reinterpret unsupported operations as supported ones.
- For example, standardize, normalize, merge, combine, create category, bucketize, log transform, encode, and derive new columns are unsupported and must return {{"actions": []}} unless another clearly supported action is also present.
Dataset Metadata:
{json.dumps(column_info, indent=2)}

User Request:
{user_request}
"""

        # response = requests.post(
        #     OLLAMA_URL,
        #     json={
        #         "model": MODEL_NAME,
        #         "prompt": prompt,
        #         "stream": False
        #     },
        #     timeout=120
        # )
        # response.raise_for_status()

        # data = response.json()
        # raw_text = data.get("response", "").strip()
        raw_text = get_groq_response(prompt)
        clean_json = extract_json(raw_text)
        plan = json.loads(clean_json)

        return plan, None

    except Exception as e:
        return None, str(e)