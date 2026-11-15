# AI Personal Financial Advisor — Financial Processing and Cloud Benchmarks

## Overview

I developed the financial processing, distributed data aggregation, and MCP financial tool components for my ENGR-E516 Cloud Computing team project.

My implementation processes synthetic BankSim transaction data using Pandas and Apache Spark, validates aggregation correctness, and exposes financial reporting functions through the Model Context Protocol (MCP).

I deployed and benchmarked the processing pipeline on Indiana University's Jetstream2 cloud infrastructure.

## Technologies

- Python 3.10
- Pandas 2.3.3
- Apache Spark / PySpark 3.5.6
- Hadoop HDFS
- Model Context Protocol (MCP)
- Streamable HTTP and stdio transports
- Jetstream2 cloud virtual machines

## Financial Processing

I implemented customer-level and category-level transaction aggregation, including transaction counts, total spending, and average transaction amounts.

I created equivalent Pandas and PySpark processing implementations and validated their consistency through automated tests.

## Distributed Cloud Infrastructure

I used three Jetstream2 virtual machines consisting of one Spark master and two Spark workers.

I configured Hadoop HDFS for distributed dataset storage and verified that both Spark workers executed financial processing tasks.

## Performance Evaluation

I benchmarked financial aggregation using datasets containing 10,000, 100,000, and 1,000,000 transactions.

### Pandas and Spark Results

| Transactions | Pandas Mean | Spark 1 Core | Spark 2 Cores |
|---|---:|---:|---:|
| 10,000 | 0.015 s | 1.378 s | 1.334 s |
| 100,000 | 0.042 s | 1.634 s | 1.547 s |
| 1,000,000 | 0.234 s | 2.561 s | 2.254 s |

Each configuration was measured across five executions.

At one million transactions, the two-core Spark configuration achieved approximately 1.14x speedup over the one-core configuration.

I observed that Pandas was substantially faster for these relatively small, in-memory workloads. Spark provided distributed execution and increasing benefits from additional compute resources as the workload grew.

These measurements exclude initial dataset loading. The Pandas and Spark timing boundaries are similar but not identical, so I treat the comparison as observed application performance rather than an isolated framework benchmark.

## MCP Financial Tools

I implemented two MCP tools:

- `get_customer_spending(customer_id)` — Returns spending totals and category breakdowns for a customer.
- `summarize_category(category)` — Returns transaction counts, total spending, and customer counts.

I validated both tools through an MCP stdio client and an HTTP MCP client.

The HTTP implementation uses Streamable HTTP and supports configurable network binding through `E516_MCP_HOST` and `E516_MCP_PORT`.

The server uses synthetic financial data. Network access controls and authentication must be addressed before deployment with sensitive financial information.

## Validation

I ran six automated correctness tests, all of which passed on Jetstream2.

I also verified distributed Spark task execution across both worker VMs and successful financial tool invocation through MCP.

## Repository Structure

- `src/` — Financial processing, reporting, PySpark, and MCP implementations
- `scripts/` — Dataset preparation and benchmarking
- `tests/` — Automated correctness and Spark runtime tests
- `benchmarks/` — Recorded benchmark measurements and analysis
- `results/` — Example financial reporting output
- `requirements*.txt` — Python dependencies

## Project Scope

This repository documents my contribution to the larger AI Personal Financial Advisor team project. Integration with the LangGraph agent, orchestration services, frontend, and model inference components is coordinated with the other team members.
