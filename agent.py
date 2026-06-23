import anthropic
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

# --- The actual tools (code that runs) ---
def calculator(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}. Write it as valid Python, e.g. 240 * 0.15 for '15% of 240'."

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# Map names -> functions so we can run whatever the model picks
TOOL_FUNCTIONS = {"calculator": calculator, "get_current_time": get_current_time}

# --- The schemas the model sees ---
tools = [
    {
        "name": "calculator",
        "description": "Evaluates a Python math expression like '240 * 0.15'. Use * / + - and write percentages as decimals (15% = 0.15).",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    },
    {
        "name": "get_current_time",
        "description": "Returns the current date and time.",
        "input_schema": {"type": "object", "properties": {}}
    }
]

messages = [{"role": "user", "content": "What's the current date, and what is 15% of 240?"}]

# --- The agent loop ---
while True:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        tools=tools,
        messages=messages
    )

    if response.stop_reason != "tool_use":
        print(response.content[0].text)
        break

    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            output = TOOL_FUNCTIONS[block.name](**block.input)
            print(f"[ran {block.name}({block.input}) -> {output}]")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output
            })
    messages.append({"role": "user", "content": tool_results})