import streamlit as st
import chromadb
import anthropic
import os
from dotenv import load_dotenv

# --- API key: .env locally, st.secrets when deployed ---
load_dotenv(override=True)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=api_key)

# --- Build the vector store ONCE (cached) ---
@st.cache_resource
def build_collection():
    db = chromadb.Client()
    collection = db.get_or_create_collection("crypto")
    with open("crypto_knowledge.txt", encoding="utf-8") as f:
        chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
    collection.add(documents=chunks, ids=[str(i) for i in range(len(chunks))])
    return collection

collection = build_collection()

# --- Tools ---
def search_documents(query):
    results = collection.query(query_texts=[query], n_results=2)
    return "\n\n".join(results["documents"][0])

def calculator(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}. Write it as valid Python, e.g. 500 * 0.02."

TOOL_FUNCTIONS = {"search_documents": search_documents, "calculator": calculator}

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

# --- The agent loop, now STREAMING the final answer ---
def run(question, tools_used):
    messages = [{"role": "user", "content": question}]
    while True:
        with client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=SYSTEM,
            tools=tools,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text                      # stream text to the UI as it's generated
            final = stream.get_final_message()  # full message, so we can check for tools

        if final.stop_reason != "tool_use":
            return  # the final answer already streamed above — done

        messages.append({"role": "assistant", "content": final.content})
        tool_results = []
        for block in final.content:
            if block.type == "tool_use":
                output = TOOL_FUNCTIONS[block.name](**block.input)
                tools_used.append(f"{block.name}({block.input})")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })
        messages.append({"role": "user", "content": tool_results})
# --- UI ---
st.title("🪙 Crypto Trading Study Assistant")
st.caption("Ask about crypto concepts or trading math — the agent searches your notes and calculates.")

# Chat history must live in session_state to survive Streamlit's reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the conversation so far
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new input
if question := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        tools_used = []
        answer = st.write_stream(run(question, tools_used))   # streams live, returns full text
        if tools_used:
            with st.expander("🔧 Tools used"):
                for t in tools_used:
                    st.write(f"- {t}")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    