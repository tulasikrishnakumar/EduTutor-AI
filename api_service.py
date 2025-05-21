import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def call_openrouter_api(prompt: str, model: str = "meta-llama/llama-3.3-8b-instruct:free") -> str:
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "EduTutorAI"
        },
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content
