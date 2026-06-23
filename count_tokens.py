import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[{"role": "user", "content": "Explain photosynthesis in 3 sentences."}]
)

print(response.content[0].text)
print("---")
print("Input tokens:", response.usage.input_tokens)
print("Output tokens:", response.usage.output_tokens)

#final commit test
print("Final commit test")