import streamlit as st
import chromadb
import anthropic
import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
ai = anthropic.Anthropic(api_key=api_key)

THRESHOLD = 1.5  # chunks farther than this are treated as irrelevant — TUNE THIS

@st.cache_resource
def build_collection():
    with open("knowledge.txt", encoding="utf-8") as f:
        chunks = [c.strip() for c in f.read().split("\n\n") if c.strip()]
    db = chromadb.Client()
    collection = db.get_or_create_collection("docs")
    collection.add(documents=chunks, ids=[str(i) for i in range(len(chunks))])
    return collection

collection = build_collection()

st.title("Chat with your documents")
question = st.text_input("Ask a question:")

if st.button("Ask") and question:
    results = collection.query(query_texts=[question], n_results=2)
    docs = results["documents"][0]
    distances = results["distances"][0]

    # keep only chunks close enough to be relevant
    relevant = [doc for doc, dist in zip(docs, distances) if dist < THRESHOLD]

    st.write("### Answer")
    if not relevant:
        st.write("I don't have anything relevant to that in my documents.")
    else:
        context = "\n\n".join(relevant)
        prompt = f"""Answer the question using ONLY the context below. If the answer isn't there, say you don't know.

Context:
{context}

Question: {question}"""
        response = ai.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        st.write(response.content[0].text)

    with st.expander("Retrieved chunks (with distances)"):
        for doc, dist in zip(docs, distances):
            mark = "✅ used" if dist < THRESHOLD else "❌ filtered"
            st.write(f"**[{dist:.2f}] {mark}** — {doc}")