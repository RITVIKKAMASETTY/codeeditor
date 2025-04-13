from fastapi import FastAPI, Body
from ollama import Client

app = FastAPI()

# Initialize Ollama client
client = Client(host='http://localhost:11434')

# Pull model once when app starts (only needed if not already pulled)
client.pull('gemma:2b')

@app.post("/chat")
def chat(message: str = Body(..., description="Chat Message")):
    response = client.chat(
        model="gemma:2b",
        messages=[{"role": "user", "content": message}]
    )
    return {"response": response['message']['content']}
