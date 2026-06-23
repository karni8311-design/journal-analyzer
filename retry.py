import anthropic
import time
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

def ask_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except anthropic.APIError as e:
            wait = 2 ** attempt  # 1s, then 2s, then 4s
            print(f"Attempt {attempt + 1} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)
    return "Failed after all retries."

print(ask_with_retry("tell me who is my father in one sentence."))