import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[{"role": "user", "content": "Write a short paragraph about why the ocean is blue."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()  # final newline