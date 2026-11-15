"""Ordinary financial computation functions for Matthew's agent/tool layer.

No hosted LLM, LangGraph, or MCP dependency is required here. The team's MCP
provider can call these functions; see src/mcp_server.py for an optional bridge.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from process_transactions import load_transactions, aggregate_transactions
from generate_report import generate_report


@lru_cache(maxsize=1)
def _aggregated():
    return aggregate_transactions(load_transactions())


def get_customer_spending(customer_id: str) -> dict[str, Any]:
    """Return deterministic spending totals per category for a BankSim customer."""
    customer_id = customer_id.strip()
    if not customer_id:
        raise ValueError("customer_id must not be blank")
    data = _aggregated()
    if customer_id not in data.index.get_level_values("customer"):
        raise ValueError("Customer ID not found in the dataset")
    return generate_report(customer_id, data)


def summarize_category(category: str) -> dict[str, Any]:
    """Return transaction count and spending total for a category."""
    category = category.strip()
    if not category:
        raise ValueError("category must not be blank")
    data = _aggregated()
    try:
        subset = data.xs(category, level="category")
    except KeyError:
        raise ValueError("Category not found in the dataset") from None
    return {
        "category": category,
        "transactions": int(subset["transactions"].sum()),
        "total_spending": round(float(subset["total_spending"].sum()), 2),
        "customer_count": int(len(subset)),
        "note": "Synthetic BankSim data; not a live financial account.",
    }
