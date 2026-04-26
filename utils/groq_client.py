import streamlit as st
from groq import Groq


def get_groq_response(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI data analyst. Return only the requested output."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()