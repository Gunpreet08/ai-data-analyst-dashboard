import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def generate_ai_summary(df, rule_based_insights, correlation_insight=None):
    """
    Generate an AI summary using locally running Ollama.
    Returns:
        summary_text, error_message
    """
    try:
        numeric_df = df.select_dtypes(include=["number"])

        if numeric_df.empty:
            return "No numeric data available for AI summary.", None

        numeric_summary = numeric_df.describe().to_string()
        insights_text = "\n".join(f"- {insight}" for insight in rule_based_insights)

        prompt = f"""
You are a helpful data analyst assistant.

Based on the dataset statistics and insights below, write a short professional summary in 5 to 7 lines.

Rules:
- Keep the language simple, clear, and professional.
- Do not invent facts.
- Mention only the most important patterns.
- Write like a business analyst summarizing findings.

Numeric Summary:
{numeric_summary}

Rule-Based Insights:
{insights_text}

Correlation Insight:
{correlation_insight if correlation_insight else "No correlation insight available."}

Now write the final summary.
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

        return data.get("response", "").strip(), None

    except Exception as e:
        return None, str(e)