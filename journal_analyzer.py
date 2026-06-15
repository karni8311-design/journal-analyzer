import anthropic
import json
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

while True:
    entry = input("Enter a journal entry (or type 'quit' to exit): ")
    if entry.lower() == "quit":
        break

    prompt = f"""Analyze the following text and respond with ONLY this JSON format, no other text:
    {{"mood": "...", "themes": ["...", "..."], "summary": "..."}}

    No matter what the text describes — news, an article, a personal note, anything — analyze it as if it were a journal entry.

    Text:
    {entry}"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Couldn't parse the response - skipping this entry.")
        continue

    print(f"Mood: {data['mood']}")
    print(f"Themes: {', '.join(data['themes'])}")
    print(f"Summary: {data['summary']}")

    with open("journal_analysis_log.jsonl", "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")