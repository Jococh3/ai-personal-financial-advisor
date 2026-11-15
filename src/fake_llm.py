import json
import os
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# A stand-in for the SGLang server, for testing without a GPU.
# It answers in the same format, after a pretend "thinking" delay.
delay = float(os.getenv("DELAY", "0.5"))


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the prompt the agent sent
        size = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(size))
        prompt = body["messages"][0]["content"]
        question = prompt.split("Question:")[-1].lower()
        time.sleep(delay)

        # Parse step: reply with one word
        if "one word" in prompt:
            text = "spending"
            if "suspicious" in question or "fraud" in question:
                text = "fraud"
        # Write step: repeat the first fact, so we can see it worked
        else:
            facts = prompt.split("Facts:\n")[1]
            text = "(fake advice) " + facts.split("\n")[0]

        # Send the reply back the way SGLang would
        data = json.dumps({"choices": [{"message": {"content": text}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # Keep the terminal quiet
    def log_message(self, *args):
        pass


print("Fake model server running on port 30000")
ThreadingHTTPServer(("", 30000), Handler).serve_forever()
