import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

def ask(prompt):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def judge(question, answer):
    prompt = f"""You are grading an AI's answer. Rate it 1-5 for accuracy and helpfulness.

Question: {question}
Answer: {answer}

Respond with ONLY a number 1-5, a dash, then a short reason. Example: "4 - correct but missed a detail"."""
    return ask(prompt)

question = "What is the capital of Australia?"
answer = ask(question)
print("Answer:", answer)
print("Grade:", judge(question, answer))