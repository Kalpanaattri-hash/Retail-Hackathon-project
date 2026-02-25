# API Documentation

## Base URL

**Local**: `http://localhost:8000`

**CORS**: Enabled for `localhost:*`, adjust in `app/main.py` for production.

---

## Endpoints

### 1. Chat (NL to SQL)

**`POST /chat`**

Send a natural language question, get SQL-powered insights.

#### Request

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were total sales last month?"}'
```

**Body Schema:**

```json
{
  "question": "string (required, 3-500 chars)"
}
```

#### Response (200 OK)

```json
{
  "answer": "Total sales last month were $125,430 across 542 transactions.",
  "generated_sql": "SELECT SUM(revenue) as total_sales, COUNT(*) as transactions FROM sales WHERE sale_date >= CURRENT_DATE - INTERVAL '1 month' LIMIT 100",
  "data_preview": [
    {
      "total_sales": 125430.50,
      "transactions": 542
    }
  ]
}
```

**Response Schema:**

```typescript
{
  "answer": "string",           // Business-friendly summary
  "generated_sql": "string",    // Executed SQL query
  "data_preview": [             // First 20 rows
    {
      "column_name": "value"
    }
  ]
}
```

#### Error Responses

**400 Bad Request** – Invalid/empty question

```json
{
  "error": "HTTP_ERROR",
  "detail": "Invalid generated SQL: Generated SQL is empty"
}
```

**500 Internal Server Error** – DB/Bedrock failure

```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "detail": "Database query failed"
}
```

---

### 2. Health Check

**`GET /health`**

Verify API is running.

#### Request

```bash
curl "http://localhost:8000/health"
```

#### Response (200 OK)

```json
{
  "status": "ok",
  "service": "Sales Analytics Chatbot",
  "environment": "development"
}
```

---

## Example Queries

### Sales Summary

**Q**: "What were total sales last month?"

**Generated SQL**:
```sql
SELECT 
  SUM(sales.revenue) as total_revenue,
  COUNT(*) as transaction_count,
  DATE_TRUNC('month', sales.sale_date) as month
FROM sales
WHERE sale_date >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY DATE_TRUNC('month', sales.sale_date)
LIMIT 100
```

---

### Regional Performance

**Q**: "Which region had highest revenue in Q4?"

**Generated SQL**:
```sql
SELECT 
  sales.region,
  SUM(sales.revenue) as total_revenue,
  COUNT(*) as transactions,
  AVG(sales.revenue) as avg_transaction_value
FROM sales
WHERE EXTRACT(QUARTER FROM sales.sale_date) = 4
GROUP BY sales.region
ORDER BY total_revenue DESC
LIMIT 100
```

---

### Top Products

**Q**: "Show top 5 products by revenue"

**Generated SQL**:
```sql
SELECT 
  products.name,
  SUM(sales.revenue) as total_revenue,
  COUNT(sales.id) as units_sold,
  AVG(sales.revenue) as avg_price
FROM sales
JOIN products ON sales.product_id = products.id
GROUP BY products.id, products.name
ORDER BY total_revenue DESC
LIMIT 5
```

---

### Quarter Comparison

**Q**: "Compare this quarter vs last quarter revenue"

**Generated SQL**:
```sql
SELECT 
  EXTRACT(QUARTER FROM sales.sale_date) as quarter,
  EXTRACT(YEAR FROM sales.sale_date) as year,
  SUM(sales.revenue) as total_revenue
FROM sales
WHERE EXTRACT(YEAR FROM sales.sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY EXTRACT(YEAR FROM sales.sale_date), EXTRACT(QUARTER FROM sales.sale_date)
ORDER BY year DESC, quarter DESC
LIMIT 100
```

---

## Data Schema

### Tables

#### `sales`

| Column | Type | Description |
|--------|------|---|
| id | INTEGER | Primary key |
| product_id | INTEGER | Foreign key → products.id |
| region | VARCHAR(100) | Sales region (North, South, East, West) |
| revenue | FLOAT | Sale amount in USD |
| quantity | INTEGER | Units sold |
| sale_date | DATE | Transaction date |

#### `products`

| Column | Type | Description |
|--------|------|---|
| id | INTEGER | Primary key |
| name | VARCHAR(255) | Product name |
| category | VARCHAR(100) | Category (Electronics, Software, Accessories) |

#### `customers`

| Column | Type | Description |
|--------|------|---|
| id | INTEGER | Primary key |
| name | VARCHAR(255) | Customer name |
| segment | VARCHAR(100) | Segment (Enterprise, SMB, Retail) |

---

## Rate Limiting & Quotas

| Limit | Value |
|-------|-------|
| Max question length | 500 characters |
| Max result rows | 100 per query |
| Conversation memory | Last 5 queries |
| Query timeout | 30 seconds |

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check question format |
| 500 | Server Error | Backend/DB offline |
| SQL blocked | Injection detected | Use NL questions, not raw SQL |
| Table not found | Unauthorized access | Check ALLOWED_TABLES |

---

## Authorization (Optional)

For production, add JWT bearer token:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"question": "..."}'
```

*(Implement in `app/routers/chat_router.py` using FastAPI's `Security` dependency)*

---

## Logging

All requests/responses logged to stdout with format:

```
2024-02-25 10:30:45 | INFO | app.routers.chat_router | POST /chat | question length: 28
2024-02-25 10:30:46 | INFO | app.services.analytics_service | Query executed: 1.2s
2024-02-25 10:30:47 | INFO | app.services.bedrock_service | Claude response: 456 tokens
```

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

response = requests.post(
    f"{BASE_URL}/chat",
    json={"question": "What were total sales last month?"},
    timeout=30
)

print(response.json())
# {
#   "answer": "...",
#   "generated_sql": "...",
#   "data_preview": [...]
# }
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000";

const response = await fetch(`${BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question: "What were total sales last month?" }),
});

const data = await response.json();
console.log(data);
```

### CURL

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"Total sales last month?"}' \
  | jq '.'
```

---

## OpenAPI Docs

FastAPI auto-generates OpenAPI specs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
