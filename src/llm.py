import os
import requests

# Where the model server is (SGLang uses port 30000 by default)
URL = os.getenv("LLM_URL", "http://localhost:30000")
MODEL = os.getenv("LLM_MODEL", "default")


def ask(prompt):
    # Send the prompt in the standard chat format SGLang understands
    msg = {"role": "user", "content": prompt}
    body = {"model": MODEL, "messages": [msg], "max_tokens": 300}
    resp = requests.post(URL + "/v1/chat/completions", json=body, timeout=120)

    # Stop with an error if the server had a problem
    resp.raise_for_status()

    # Pull the reply text out of the response
    return resp.json()["choices"][0]["message"]["content"]
