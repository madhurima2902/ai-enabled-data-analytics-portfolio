"""Banking Operations Investigation Agent.

Prototype agentic analytics assistant for the Banking Operations Analytics project.

The agent uses:
- LangGraph for workflow orchestration
- Local markdown RAG over knowledge_base files
- Template-based safe SQL generation for common banking investigations
- PostgreSQL execution for evidence
- Optional LLM-based final answer synthesis when OPENAI_API_KEY is available

Run:
    python src/banking_ops_agent.py "Why are digital channels creating more customer pain?"
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

import pandas as pd
import psycopg
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional dependency path
    ChatOpenAI = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"


class AgentState(TypedDict, total=False):
    """State object passed through the LangGraph workflow."""

    question: str
    intent: str
    retrieved_context: str
    sql: str
    sql_valid: bool
    validation_error: str
    result_markdown: str
    final_answer: str


load_dotenv(PROJECT_ROOT / ".env")


def get_db_connection() -> psycopg.Connection:
    """Create a PostgreSQL connection using environment variables."""

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "banking_analytics_db"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def normalize_tokens(text: str) -> List[str]:
    """Simple tokenizer for local keyword retrieval."""

    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def load_knowledge_chunks() -> List[Dict[str, str]]:
    """Load markdown knowledge files as coarse chunks."""

    chunks: List[Dict[str, str]] = []
    for path in KNOWLEDGE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        sections = re.split(r"\n(?=## )", text)
        for i, section in enumerate(sections):
            cleaned = section.strip()
            if cleaned:
                chunks.append({"source": f"{path.name}#section-{i + 1}", "text": cleaned})
    return chunks


def retrieve_context(question: str, top_k: int = 3) -> str:
    """Retrieve relevant context from local markdown files using token overlap."""

    query_tokens = set(normalize_tokens(question))
    scored: List[tuple[int, Dict[str, str]]] = []

    for chunk in load_knowledge_chunks():
        chunk_tokens = set(normalize_tokens(chunk["text"]))
        score = len(query_tokens.intersection(chunk_tokens))
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [chunk for score, chunk in scored[:top_k] if score > 0]

    if not selected:
        return "No directly relevant knowledge-base context was retrieved."

    return "\n\n---\n\n".join(
        f"Source: {chunk['source']}\n\n{chunk['text']}" for chunk in selected
    )


def classify_intent(question: str) -> str:
    """Classify the investigation type from the user question."""

    q = question.lower()
    if any(word in q for word in ["sla", "breach", "ticket", "team", "priority"]):
        return "sla_breach"
    if any(word in q for word in ["campaign", "conversion", "engagement", "offer"]):
        return "campaign_conversion"
    if any(word in q for word in ["complaint", "pain", "customer issue", "resolution"]):
        if any(word in q for word in ["digital", "channel", "mobile", "internet"]):
            return "digital_channel_pain"
        return "complaint_drivers"
    if any(word in q for word in ["digital", "channel", "mobile", "internet", "failure"]):
        return "digital_channel_pain"
    return "digital_channel_pain"


def generate_sql_for_intent(intent: str) -> str:
    """Generate safe read-only SQL for the classified intent."""

    if intent == "digital_channel_pain":
        return """
WITH transaction_summary AS (
    SELECT
        dc.channel_name,
        dc.is_digital,
        SUM(ft.transaction_count) AS total_transactions,
        SUM(ft.failed_transaction_count) AS failed_transactions,
        SUM(ft.successful_transaction_count) AS successful_transactions,
        SUM(ft.amount) AS total_transaction_amount
    FROM warehouse.fact_transactions ft
    JOIN warehouse.dim_channel dc
        ON ft.channel_key = dc.channel_key
    GROUP BY dc.channel_name, dc.is_digital
),
complaint_summary AS (
    SELECT
        dc.channel_name,
        SUM(fc.complaint_count) AS total_complaints,
        SUM(fc.open_complaint_count) AS open_complaints,
        SUM(fc.resolved_complaint_count) AS resolved_complaints,
        AVG(fc.resolution_days) AS avg_resolution_days
    FROM warehouse.fact_complaints fc
    JOIN warehouse.dim_channel dc
        ON fc.channel_key = dc.channel_key
    GROUP BY dc.channel_name
)
SELECT
    ts.channel_name,
    ts.is_digital,
    ts.total_transactions,
    ts.failed_transactions,
    ROUND(100.0 * ts.failed_transactions / NULLIF(ts.total_transactions, 0), 2) AS transaction_failure_rate_pct,
    COALESCE(cs.total_complaints, 0) AS total_complaints,
    ROUND(1000.0 * COALESCE(cs.total_complaints, 0) / NULLIF(ts.total_transactions, 0), 2) AS complaints_per_1000_transactions,
    COALESCE(cs.open_complaints, 0) AS open_complaints,
    COALESCE(cs.resolved_complaints, 0) AS resolved_complaints,
    ROUND(COALESCE(cs.avg_resolution_days, 0)::numeric, 2) AS avg_resolution_days
FROM transaction_summary ts
LEFT JOIN complaint_summary cs
    ON ts.channel_name = cs.channel_name
ORDER BY complaints_per_1000_transactions DESC, transaction_failure_rate_pct DESC;
""".strip()

    if intent == "sla_breach":
        return """
SELECT
    assigned_team,
    ticket_priority,
    SUM(ticket_count) AS total_tickets,
    SUM(sla_breached_count) AS breached_tickets,
    SUM(sla_met_count) AS sla_met_tickets,
    ROUND(100.0 * SUM(sla_breached_count) / NULLIF(SUM(ticket_count), 0), 2) AS sla_breach_rate_pct,
    ROUND(100.0 * SUM(sla_met_count) / NULLIF(SUM(ticket_count), 0), 2) AS sla_met_rate_pct
FROM warehouse.fact_sla_tickets
GROUP BY assigned_team, ticket_priority
HAVING SUM(ticket_count) > 0
ORDER BY sla_breach_rate_pct DESC, total_tickets DESC;
""".strip()

    if intent == "complaint_drivers":
        return """
SELECT
    fc.complaint_category,
    dc.channel_name,
    dp.product_name,
    SUM(fc.complaint_count) AS total_complaints,
    SUM(fc.open_complaint_count) AS open_complaints,
    SUM(fc.resolved_complaint_count) AS resolved_complaints,
    ROUND(100.0 * SUM(fc.resolved_complaint_count) / NULLIF(SUM(fc.complaint_count), 0), 2) AS complaint_resolution_rate_pct,
    ROUND(AVG(fc.resolution_days)::numeric, 2) AS avg_resolution_days
FROM warehouse.fact_complaints fc
JOIN warehouse.dim_channel dc
    ON fc.channel_key = dc.channel_key
JOIN warehouse.dim_product dp
    ON fc.product_key = dp.product_key
GROUP BY fc.complaint_category, dc.channel_name, dp.product_name
HAVING SUM(fc.complaint_count) > 0
ORDER BY total_complaints DESC, avg_resolution_days DESC
LIMIT 20;
""".strip()

    if intent == "campaign_conversion":
        return """
SELECT
    campaign_type,
    SUM(campaign_sent_count) AS campaign_offers_sent,
    SUM(engaged_count) AS engaged_customers,
    SUM(converted_count) AS converted_customers,
    ROUND(100.0 * SUM(engaged_count) / NULLIF(SUM(campaign_sent_count), 0), 2) AS engagement_rate_pct,
    ROUND(100.0 * SUM(converted_count) / NULLIF(SUM(campaign_sent_count), 0), 2) AS conversion_rate_pct
FROM warehouse.fact_campaigns
GROUP BY campaign_type
HAVING SUM(campaign_sent_count) > 0
ORDER BY conversion_rate_pct ASC, campaign_offers_sent DESC;
""".strip()

    raise ValueError(f"Unsupported intent: {intent}")


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate that SQL is read-only and safe for portfolio demo usage."""

    cleaned = sql.strip().lower()

    if not (cleaned.startswith("select") or cleaned.startswith("with")):
        return False, "Only SELECT or WITH read-only statements are allowed."

    blocked_patterns = [
        r"\binsert\b",
        r"\bupdate\b",
        r"\bdelete\b",
        r"\bdrop\b",
        r"\balter\b",
        r"\btruncate\b",
        r"\bcreate\b",
        r"\bgrant\b",
        r"\brevoke\b",
        r"\bcopy\b",
        r"\bcall\b",
        r"\bexecute\b",
    ]

    for pattern in blocked_patterns:
        if re.search(pattern, cleaned):
            return False, f"Blocked SQL keyword detected: {pattern}"

    if cleaned.count(";") > 1:
        return False, "Multiple SQL statements are not allowed."

    return True, "SQL passed read-only validation."


def execute_sql(sql: str) -> pd.DataFrame:
    """Execute SQL and return a pandas DataFrame."""

    with get_db_connection() as conn:
        return pd.read_sql_query(sql, conn)


def dataframe_to_markdown(df: pd.DataFrame, max_rows: int = 12) -> str:
    """Convert result DataFrame to markdown for final answer."""

    if df.empty:
        return "No rows returned."
    return df.head(max_rows).to_markdown(index=False)


def optional_llm_summary(question: str, context: str, sql: str, result_markdown: str) -> Optional[str]:
    """Use an LLM for answer synthesis if OPENAI_API_KEY is configured."""

    if not os.getenv("OPENAI_API_KEY") or ChatOpenAI is None:
        return None

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model_name, temperature=0)

    prompt = f"""
You are a banking operations analytics assistant.

Question:
{question}

Retrieved KPI / SLA / business context:
{context}

Validated SQL used:
{sql}

SQL result:
{result_markdown}

Write a concise investigation answer with these sections:
1. Finding
2. Evidence
3. Likely root cause
4. Recommended action
5. Next monitoring metric

Be honest that this is a synthetic portfolio dataset.
""".strip()

    response = llm.invoke(prompt)
    return getattr(response, "content", str(response))


def deterministic_summary(state: AgentState) -> str:
    """Fallback final answer when no LLM key is available."""

    intent = state.get("intent", "unknown")
    question = state.get("question", "")
    sql = state.get("sql", "")
    result = state.get("result_markdown", "")

    if intent == "digital_channel_pain":
        finding = (
            "The investigation compares channels using transaction failure rate and "
            "complaints per 1,000 transactions, which is stronger than raw complaint count alone."
        )
        recommendation = (
            "Prioritize reliability review for the channel with the highest combined failure rate "
            "and complaint burden. Track failure rate, complaints per 1,000 transactions, and open complaints monthly."
        )
    elif intent == "sla_breach":
        finding = "The investigation ranks assigned teams and ticket priorities by SLA breach rate."
        recommendation = (
            "Review capacity, routing, and escalation processes for teams with high SLA breach rate "
            "and meaningful ticket volume."
        )
    elif intent == "complaint_drivers":
        finding = "The investigation ranks complaint categories by volume, open workload, and resolution speed."
        recommendation = (
            "Prioritize high-volume complaint categories with slower resolution time and open backlog."
        )
    elif intent == "campaign_conversion":
        finding = "The investigation compares campaign types by engagement and conversion performance."
        recommendation = (
            "Review campaign types where engagement does not convert into product uptake; refine targeting and offer fit."
        )
    else:
        finding = "The investigation generated a read-only SQL query and returned evidence from the warehouse."
        recommendation = "Review the highest-risk segment shown in the SQL result."

    return f"""
## Question

{question}

## Finding

{finding}

## Evidence from SQL Result

{result}

## Validated SQL Used

```sql
{sql}
```

## Likely Root Cause

The likely driver should be inferred from the highest-risk rows in the SQL result, focusing on where volume and rate-based risk are both elevated.

## Recommended Action

{recommendation}

## Next Monitoring Metric

Use the same KPI monthly after the February/March incremental load is added, and compare month-over-month movement.
""".strip()


def classify_node(state: AgentState) -> AgentState:
    return {"intent": classify_intent(state["question"])}


def retrieve_node(state: AgentState) -> AgentState:
    return {"retrieved_context": retrieve_context(state["question"])}


def sql_generation_node(state: AgentState) -> AgentState:
    return {"sql": generate_sql_for_intent(state["intent"])}


def sql_validation_node(state: AgentState) -> AgentState:
    valid, message = validate_sql(state["sql"])
    return {"sql_valid": valid, "validation_error": message}


def sql_execution_node(state: AgentState) -> AgentState:
    if not state.get("sql_valid"):
        return {"result_markdown": f"SQL validation failed: {state.get('validation_error')}"}

    df = execute_sql(state["sql"])
    return {"result_markdown": dataframe_to_markdown(df)}


def synthesis_node(state: AgentState) -> AgentState:
    llm_answer = optional_llm_summary(
        question=state["question"],
        context=state.get("retrieved_context", ""),
        sql=state.get("sql", ""),
        result_markdown=state.get("result_markdown", ""),
    )

    return {"final_answer": llm_answer or deterministic_summary(state)}


def build_graph():
    """Build and compile the LangGraph workflow."""

    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("retrieve_context", retrieve_node)
    graph.add_node("generate_sql", sql_generation_node)
    graph.add_node("validate_sql", sql_validation_node)
    graph.add_node("execute_sql", sql_execution_node)
    graph.add_node("synthesize_answer", synthesis_node)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_edge("validate_sql", "execute_sql")
    graph.add_edge("execute_sql", "synthesize_answer")
    graph.add_edge("synthesize_answer", END)

    return graph.compile()


def run(question: str) -> str:
    """Run the agent for a single question."""

    app = build_graph()
    result = app.invoke({"question": question})
    return result["final_answer"]


def main() -> None:
    if len(sys.argv) < 2:
        print("Please provide a question.")
        print('Example: python src/banking_ops_agent.py "Why are digital channels creating more customer pain?"')
        raise SystemExit(1)

    question = " ".join(sys.argv[1:])
    print(run(question))


if __name__ == "__main__":
    main()
