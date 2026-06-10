import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

FREE_MODELS = [
    "openrouter/auto",
    "qwen/qwen3-coder:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
]

def call_llm(prompt, system_prompt=None, json_mode=False):
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})
    
    for model in FREE_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1
            )
            content = response.choices[0].message.content
            return content.strip()
        except Exception as e:
            print(f"Model {model} failed: {str(e)[:60]}")
            continue
    
    return None