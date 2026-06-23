import chromadb
import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

# --- Build the vector store from your crypto knowledge base ---
db = chromadb.Client()
collection = db.get_or_create_collection("crypto")
with open("crypto_knowledge.txt", encoding="utf-8") as f:
    chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
collection.add(documents=chunks, ids=[str(i) for i in range(len(chunks))])

# --- Tool functions ---
def search_documents(query):
    results = collection.query(query_texts=[query], n_results=2)
    return "\n\n".join(results["documents"][0])

def calculator(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}. Write it as valid Python, e.g. 500 * 0.02."

TOOL_FUNCTIONS = {"search_documents": search_documents, "calculator": calculator}

# --- Tool schemas the model sees ---
tools = [
    {
        "name": "search_documents",
        "description": "Searches the crypto trading knowledge base and returns relevant passages. Use this for any question about crypto concepts, terms, or how trading works.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What to look up"}},
            "required": ["query"]
        }
    },
    {
        "name": "calculator",
        "description": "Evaluates a Python math expression like '500 * 0.02'. Use * / + - and write percentages as decimals (2% = 0.02).",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    }
]

SYSTEM = "You are a crypto trading study assistant. Use search_documents to ground your answers in the knowledge base, and calculator for any math. If the documents don't cover something, say so."

# --- The agent loop ---
def run(question):
    messages = [{"role": "user", "content": question}]
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=SYSTEM,
            tools=tools,
            messages=messages
        )
        if response.stop_reason != "tool_use":
            return response.content[0].text
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = TOOL_FUNCTIONS[block.name](**block.input)
                print(f"[ran {block.name}({block.input})]")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })
        messages.append({"role": "user", "content": tool_results})

# --- Try it ---
print(run("What is leverage, and what position size does 10x leverage give me on $500?"))