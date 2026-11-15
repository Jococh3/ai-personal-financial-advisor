import sys
import time
from agent import df, spending, check_fraud
from tasks import advise

# How many jobs to send (default 20)
n = 20
if len(sys.argv) > 1:
    n = int(sys.argv[1])

# One job per customer, alternating between two questions
custs = df["customer"].str.strip("'").unique()[:n]
questions = ["How is my spending looking?", "Are there any suspicious charges on my account?"]

# Put every job on the queue at once
start = time.time()
jobs = []
for i in range(n):
    jobs.append(advise.delay(custs[i], questions[i % 2]))

# Wait for all of them to finish
results = []
for job in jobs:
    results.append(job.get(timeout=600))
total = time.time() - start

# Check each job used its own customer's data (no mix-ups between users)
bad = 0
secs = 0
for i, res in enumerate(results):
    if res["intent"] == "fraud":
        want = check_fraud({"cust": custs[i]})["facts"]
    else:
        want = spending({"cust": custs[i]})["facts"]
    if res["cust"] != custs[i] or res["facts"] != want:
        bad += 1
    secs += res["secs"]

# Print the results
print(f"Jobs: {n}  Total: {total:.1f}s  Jobs/sec: {n / total:.2f}")
print(f"Avg job: {secs / n:.2f}s  Mix-ups: {bad}")
print("Sample answer:", results[0]["answer"])
