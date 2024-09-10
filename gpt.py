import openai
from openai import OpenAI
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def get_fix(string):
    query = string
    messages = [{"role": "user", "content": query}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content
