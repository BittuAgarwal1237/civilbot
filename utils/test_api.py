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

def call_llm(prompt):
    for model in FREE_MODELS:
        try:
            print(f"Trying: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            print(f"✓ Success: {model}")
            return content, model
        except Exception as e:
            print(f"✗ Failed: {str(e)[:80]}")
            continue
    return None, None

if __name__ == "__main__":
    result, used_model = call_llm("Say exactly this: API is working")
    if result:
        print(f"\nOutput: {result}")
        print(f"Model used: {used_model}")
    else:
        print("All models failed")