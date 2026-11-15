# Agent layer

A user asks a question. The question goes on a Redis queue as a job. Celery workers (on as many VMs as we want) pick up jobs and run them through the agent. The agent gets spending numbers from Joshua's MCP server, and the answer is saved back in Redis.

The agent has 4 steps:

```
parse (model call 1) -> spending OR fraud -> look up rules -> write answer (model call 2)
```

1. **parse**: the model decides if the question is about spending or fraud.
2. **spending**: calls Joshua's MCP tools `get_customer_spending` and `summarize_category`. **fraud**: the customer's fraud-flagged charges.
3. **lookup**: finds matching financial rules in `data/rules.txt` (the RAG part).
4. **write**: the model writes the answer using only those facts and rules.

## The machines

```
            Redis VM (job queue)
                  |
  Worker VM 1, Worker VM 2, ...  (run the agent)
         |                 |
  MCP VM (Joshua's tools)  GPU VM (SGLang model)
```

## New files

| File | What it does |
|---|---|
| `src/agent.py` | The 4 steps, connected with LangGraph. |
| `src/tools.py` | Calls Joshua's MCP tools over HTTP. |
| `src/llm.py` | Sends a prompt to the model server (SGLang). |
| `src/rules.py` | Picks the rules whose topics match the question. |
| `data/rules.txt` | Placeholder rules. Du's rules go here. |
| `src/tasks.py` | The Celery job: one job = one customer's question. |
| `src/load_test.py` | Sends N jobs at once, times them, checks no users got mixed up. |
| `src/fake_llm.py` | A fake model server, for testing without a GPU. |

Needs Joshua's repo (his `src/` files, including `mcp_http_server.py`), and the original BankSim CSV in `data/`.

## Run it on your laptop

You need Redis running (Mac: `brew install redis`, then `redis-server`).

```
# install
pip install -r requirements-agents.txt
cd src

# terminal 1: Joshua's MCP server, running on your machine
python mcp_http_server.py

# terminal 2: fake model server
python fake_llm.py

# try one question (no queue)
python agent.py C1000148617 "How is my spending looking?"

# terminal 3: a worker that runs 4 jobs at a time
celery -A tasks worker --pool=threads --concurrency=4

# terminal 4: send 20 jobs and time them
python load_test.py 20
```

## On Jetstream2

- **Redis VM**: `sudo apt install redis-server`. In `/etc/redis/redis.conf` set `bind 0.0.0.0` and a `requirepass`.
- **MCP server**: Joshua's, already running on his master VM at `http://10.4.36.195:8000/mcp`. That's a private address, so it only works from VMs on the same Jetstream2 network.
- **GPU VM**: runs SGLang, for example
  `python -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 30000`
- **Worker VMs**: copy the repo and dataset, then:
  ```
  export REDIS_URL=redis://:PASSWORD@REDIS_VM_IP:6379/0
  export MCP_URL=http://10.4.36.195:8000/mcp
  export LLM_URL=http://GPU_VM_IP:30000
  celery -A tasks worker --pool=threads --concurrency=4
  ```

Security: the MCP server has no password, so in UFW allow ports 6379 and 8000 only from our own VMs, never from everywhere.

## Test results (fake model, 0.5 s per call, 2 calls per job, MCP over HTTP)

| Workers | Jobs | Time | Jobs/sec | Mix-ups |
|---|---|---|---|---|
| 1 | 20 | 20.9 s | 0.96 | 0 |
| 4 | 20 | 5.4 s | 3.68 | 0 |
| 2 processes x 2 (like 2 VMs) | 40 | 10.8 s | 3.71 | 0 |

The two MCP calls add about 0.04 s per job. With a real model on one GPU, the speedup will level off once the GPU is busy. Measuring where that happens is a good result for the report.

## Notes

- Joshua's tools need the quote marks that are in the data: `'C1000148617'`, not `C1000148617`. `agent.py` adds them.
- The fraud step still reads the CSV directly. If Joshua adds a fraud tool to his MCP server, the agent won't need the data file at all.
- **Du**: replace `data/rules.txt`. Format: topic words, a colon, then the rule.
- **Anish**: the API sends a job with `advise.delay(customer, question)` and gets the answer with `.get()`.
