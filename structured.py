import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

# The "tool" is really just your output schema
tools = [
    {
        "name": "record_analysis",
        "description": "Records the analysis of a journal entry.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mood": {"type": "string", "description": "The overall mood"},
                "themes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key themes"
                },
                "summary": {"type": "string", "description": "A one-sentence summary"}
            },
            "required": ["mood", "themes", "summary"]
        }
    }
]

entry = "Today was rough. Fought with my sister and couldn't focus at work. Went for a run in the evening and felt a bit better."

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    tools=tools,
    tool_choice={"type": "tool", "name": "record_analysis"},  # FORCE the model to use this tool
    messages=[{"role": "user", "content": f"Analyze this journal entry: {entry}"}]
)

# Arguments are guaranteed to match the schema — no parsing, no fences, no try/except
data = response.content[0].input
print("Mood:", data["mood"])
print("Themes:", ", ".join(data["themes"]))
print("Summary:", data["summary"])