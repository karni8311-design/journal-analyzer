import os
import streamlit as st
import anthropic
import json
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.secrets["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key = api_key)

st.title("Journal Analyzer")
entry = st.text_area("Write your journal entry:")

if st.button("Analyze") and entry:
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
    # ...same fence-stripping + json.loads +try/except as before...
    
    text = response.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        st.error("Couldn't parse the response - try again.")
        st.stop()
        
    with open("journal_analysis_log.jsonl", "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")
    st.write(f"**Mood:** {data['mood']}")
    st.write(f"**Themes:** {', '.join(data['themes'])}")
    st.write(f"**Summary:** {data['summary']}")