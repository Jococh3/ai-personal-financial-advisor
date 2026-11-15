import sys
from typing import TypedDict
from langgraph.graph import StateGraph, END
from process_transactions import load_transactions
from llm import ask
from rules import find_rules
from tools import call_tool

# Load the data once. Only the fraud step uses it;
# spending numbers come from Joshua's MCP server.
df = load_transactions()
fraud = df[df["fraud"] == 1]


# Clean up a name from the data ('es_food' becomes food)
def clean(name):
    return name.strip("'").replace("es_", "")


# Everything the agent knows while it works on one question
class State(TypedDict):
    cust: str
    q: str
    intent: str
    facts: str
    topic: str
    rules: list
    answer: str


# Step 1 (model call 1): decide what the question is about
def parse(state):
    prompt = "Is this question about 'spending' or 'fraud'? Reply with one word.\n"
    prompt += "Question: " + state["q"]
    reply = ask(prompt).lower()
    if "fraud" in reply:
        return {"intent": "fraud"}
    return {"intent": "spending"}


# Pick the next step based on the intent
def route(state):
    return state["intent"]


# Step 2a: get the customer's spending report from Joshua's MCP server
def spending(state):
    # The data keeps quote marks around ids, so we add them
    cid = "'" + state["cust"] + "'"
    rep = call_tool("get_customer_spending", {"customer_id": cid})
    if rep is None:
        return {"facts": "No transactions found.", "topic": ""}
    cats = rep["categories"]

    # One line per category, and remember the biggest one
    lines = ["Total spent: $" + str(rep["total_spending"])]
    top = None
    for cat in cats:
        count = cats[cat]["transactions"]
        spent = cats[cat]["total_spending"]
        lines.append(f"{clean(cat)}: {count} purchases, ${spent}")
        if top is None or spent > cats[top]["total_spending"]:
            top = cat

    # Compare their biggest category to other customers (Joshua's second tool)
    info = call_tool("summarize_category", {"category": top})
    avg = round(info["total_spending"] / info["customer_count"], 2)
    mine = cats[top]["total_spending"]
    diff = round(abs(mine - avg), 2)

    # Decide "more" or "less" here, because the model gets this wrong
    word = "more"
    if mine < avg:
        word = "less"
    text = f"Biggest category: {clean(top)}, ${mine}. "
    text += f"That is ${diff} {word} than the average customer (${avg})"
    lines.append(text)

    return {"facts": "\n".join(lines), "topic": clean(top)}


# Step 2b: list the customer's fraud-flagged charges
def check_fraud(state):
    cid = "'" + state["cust"] + "'"
    rows = fraud[fraud["customer"] == cid]
    total = round(rows["amount"].sum(), 2)
    lines = [f"Flagged charges: {len(rows)}, totaling ${total}"]

    # Show the first 5 flagged charges
    for i, row in rows.head(5).iterrows():
        cat = clean(row["category"])
        shop = clean(row["merchant"])
        lines.append(f"Day {row['step']}: {cat} at {shop}, ${row['amount']}")
    return {"facts": "\n".join(lines), "topic": ""}


# Step 3: find financial rules that match (the RAG part)
def lookup(state):
    text = state["q"] + " " + state["intent"] + " " + state["topic"]
    return {"rules": find_rules(text)}


# Step 4 (model call 2): write the answer
def write(state):
    prompt = "You are a friendly personal finance advisor. "
    prompt += "Answer in 3-4 sentences, using only these facts and rules.\n"
    prompt += "Facts:\n" + state["facts"] + "\n"
    prompt += "Rules:\n" + "\n".join(state["rules"]) + "\n"
    prompt += "Question: " + state["q"]
    return {"answer": ask(prompt)}


# Connect the steps: parse -> spending or fraud -> lookup -> write
steps = StateGraph(State)
steps.add_node("parse", parse)
steps.add_node("spending", spending)
steps.add_node("fraud", check_fraud)
steps.add_node("lookup", lookup)
steps.add_node("write", write)
steps.set_entry_point("parse")
steps.add_conditional_edges("parse", route)
steps.add_edge("spending", "lookup")
steps.add_edge("fraud", "lookup")
steps.add_edge("lookup", "write")
steps.add_edge("write", END)
graph = steps.compile()


# Try one question: python agent.py C1000148617 "How is my spending?"
if __name__ == "__main__":
    out = graph.invoke({"cust": sys.argv[1], "q": sys.argv[2]})
    print("Intent:", out["intent"])
    print("Facts:\n" + out["facts"])
    print("Rules:", out["rules"])
    print("Answer:", out["answer"])
