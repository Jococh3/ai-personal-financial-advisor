import os
import time
from celery import Celery
from agent import graph

# Redis holds the job queue and the finished results
url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("tasks", broker=url, backend=url)


# One job = one customer's question, run through the agent
@app.task
def advise(cust, q):
    start = time.time()
    out = graph.invoke({"cust": cust, "q": q})
    return {
        "cust": cust,
        "intent": out["intent"],
        "facts": out["facts"],
        "answer": out["answer"],
        "secs": round(time.time() - start, 2),
    }
