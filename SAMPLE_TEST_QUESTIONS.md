# Sample Test Questions for Sales Analytics Chatbot

## Quick Test Questions

These questions will work with both SQLite and RDS databases once connected.

### 1. **Total Sales**
```
Question: "What are total sales?"
Expected Response: "Total sales: $XXX,XXX.XX from XXX transactions"
SQL: SELECT SUM(revenue) as total, COUNT(*) as count FROM sales
Tests: Basic aggregation query
```

### 2. **Sales by Region**
```
Question: "Show me sales by region"
Expected Response: "Sales by region: North: $XXX,XXX.XX, South: $XXX,XXX.XX, East: $XXX,XXX.XX, West: $XXX,XXX.XX"
SQL: SELECT region, SUM(revenue) as revenue, COUNT(*) as count FROM sales GROUP BY region ORDER BY revenue DESC
Tests: GROUP BY aggregation
```

### 3. **Top Products**
```
Question: "What are the top products?"
Expected Response: "Top products: Laptop: $XXX,XXX.XX, Monitor: $XXX,XXX.XX, ..."
SQL: SELECT p.name, SUM(s.revenue) as revenue FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.name ORDER BY revenue DESC LIMIT 5
Tests: JOIN & aggregation
```

### 4. **Sales Trend**
```
Question: "Show me the sales trend"
Expected Response: "Sales trend for last 7 days: 7 records"
SQL: SELECT sale_date, SUM(revenue) as revenue FROM sales GROUP BY sale_date ORDER BY sale_date DESC LIMIT 7
Tests: Date filtering & ordering
```

### 5. **Database Summary**
```
Question: "Give me a summary"
Expected Response: "Database summary: XXX sales, $XXX,XXX.XX total revenue, $XXX.XX average"
SQL: SELECT COUNT(*) as count, SUM(revenue) as total, AVG(revenue) as avg FROM sales
Tests: Multiple aggregations
```

---

## How to Test the Chatbot

### **Using PowerShell (REST API)**

#### Test 1: Health Check
```powershell
Invoke-WebRequest http://localhost:8000/health
```

#### Test 2: Ask a Question
```powershell
$body = @{question="What are total sales?"} | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/chat `
  -Body $body `
  -ContentType "application/json" | ConvertTo-Json
```

#### Test 3: Try All Questions
```powershell
$questions = @(
    "What are total sales?",
    "Show me sales by region",
    "What are the top products?",
    "Show me the sales trend",
    "Give me a summary"
)

foreach ($q in $questions) {
    Write-Host "`n=== Question: $q ===" -ForegroundColor Green
    $body = @{question=$q} | ConvertTo-Json
    $response = Invoke-RestMethod -Method Post `
      -Uri http://localhost:8000/chat `
      -Body $body `
      -ContentType "application/json"
    Write-Host "Answer: $($response.answer)"
    Write-Host "SQL: $($response.generated_sql)"
}
```

### **Using Browser UI**

1. Open http://localhost:5173 (if frontend is running)
2. Type any question in the chat box
3. See the answer + SQL query + data preview

---

## Database Sample Data

### Products (5 total)
```
1. Laptop - Electronics
2. Monitor - Electronics
3. Mouse - Accessories
4. Keyboard - Accessories
5. Headphones - Electronics
```

### Customers (5 total)
```
1. John Smith - Enterprise
2. Sarah Johnson - SMB
3. Mike Davis - Enterprise
4. Emily Wilson - Startup
5. David Brown - SMB
```

### Regions (4 total)
```
North, South, East, West
```

### Sales Data
```
200 records over 90 days
Date range: Last 90 days
Regions: North, South, East, West
Revenue range: $100 - $1000 per transaction
```

---

## Expected Results from Sample Data

| Metric | Expected Value |
|--------|-----------------|
| Total Sales | ~$44,000 - $45,000 |
| Total Transactions | ~200 |
| Average Revenue | ~$220 - $225 |
| Region Sales | Evenly distributed across 4 regions |
| Top Product | Laptop (highest total revenue) |
| Sales Days | 90 days in range |

---

## More Advanced Questions (if using real NL→SQL)

These might work if AWS Bedrock is configured:

```
1. "How much did we sell in January?"
2. "Which region is performing best?"
3. "What's the average order value?"
4. "How many products did we sell yesterday?"
5. "Show revenue by product category"
6. "Which customer segment generates the most revenue?"
7. "What's our sales velocity (revenue per day)?"
8. "How many transactions in each region?"
```

---

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] RDS/SQLite database connected
- [ ] Health check returns 200 OK
- [ ] Can send chat questions via REST API
- [ ] Responses include: answer, SQL, data_preview
- [ ] Frontend displays chat messages and results
- [ ] All 5 sample questions work

---

## Quick Copy-Paste Tests

### Test 1: Total Sales
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat -Body (@{question="What are total sales?"} | ConvertTo-Json) -ContentType "application/json"
```

### Test 2: Top Products
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat -Body (@{question="What are the top products?"} | ConvertTo-Json) -ContentType "application/json"
```

### Test 3: Region Sales
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat -Body (@{question="Show me sales by region"} | ConvertTo-Json) -ContentType "application/json"
```

### Test 4: Trend
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat -Body (@{question="Show me the sales trend"} | ConvertTo-Json) -ContentType "application/json"
```

### Test 5: Summary
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat -Body (@{question="Give me a summary"} | ConvertTo-Json) -ContentType "application/json"
```

---

## Success Indicators

✅ You'll know it's working when:
- API returns JSON responses (not errors)
- `answer` field contains human-readable text
- `generated_sql` field shows the SQL query
- `data_preview` contains actual database records
- Numbers in answers match database data

❌ Common issues:
- "Error: Connection timeout" → RDS security group not fixed
- "No module named psycopg2" → Run `pip install psycopg2-binary`
- "Database does not exist" → Run `init_rds.py` to seed data
- "Empty results" → Check if data was inserted correctly
