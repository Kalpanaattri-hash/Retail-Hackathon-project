from datetime import datetime


def sql_generation_prompt(
    question: str,
    allowed_tables: set[str],
    recent_history: list[dict[str, str]],
) -> tuple[str, str]:
    history_text = "\n".join(
        f"- Q: {item['question']} | SQL: {item['sql']}" for item in recent_history
    )
    if not history_text:
        history_text = "- No prior conversation context"

    schema_description = """
You can query ONLY these PostgreSQL tables:
1) sales(id, product_id, region, revenue, quantity, sale_date)
2) products(id, name, category)
3) customers(id, name, segment)

Relationships:
- sales.product_id = products.id
""".strip()

    system_prompt = f"""
You are a senior SQL analyst assistant. Convert business questions to safe PostgreSQL SQL.
Rules:
- Return only valid JSON with keys: sql, rationale.
- Generate a single SELECT statement only.
- Never generate DELETE, DROP, UPDATE, INSERT, ALTER, TRUNCATE, CREATE.
- Query only allowed tables: {', '.join(sorted(allowed_tables))}.
- Include LIMIT 100 or less.
- Use accurate date logic for month/quarter/year comparisons.
- Prefer explicit column names and aliases for business readability.
""".strip()

    user_prompt = f"""
Current timestamp: {datetime.utcnow().isoformat()}Z

Database schema:
{schema_description}

Recent conversation:
{history_text}

User question:
{question}

Output format example:
{{
  "sql": "SELECT ... LIMIT 100",
  "rationale": "Brief explanation"
}}
""".strip()

    return system_prompt, user_prompt


def business_summary_prompt(question: str, sql: str, rows: list[dict]) -> tuple[str, str]:
    system_prompt = """
You are a business analytics assistant.
Summarize SQL query results in concise business language for stakeholders.
If no rows, clearly say no matching data was found.
""".strip()

    user_prompt = f"""
Question:
{question}

SQL used:
{sql}

Result rows (JSON):
{rows}

Return:
- A concise answer in 2-4 sentences
- Mention key figures if available
- Avoid technical jargon unless needed
""".strip()

    return system_prompt, user_prompt
