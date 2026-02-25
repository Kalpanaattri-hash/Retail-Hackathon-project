# Integration Examples

This file shows how to integrate the Sales Analytics Chatbot API into your applications.

## Python Integration

### Basic Usage

```python
import requests
import json

# Configuration
API_URL = "http://localhost:8000"

# Make a query
response = requests.post(
    f"{API_URL}/chat",
    json={"question": "What were total sales last month?"},
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    print(f"Answer: {result['answer']}")
    print(f"SQL: {result['generated_sql']}")
    print(f"Rows: {len(result['data_preview'])}")
else:
    print(f"Error: {response.text}")
```

### With Error Handling

```python
import requests
from typing import Optional

def ask_sales_question(question: str) -> Optional[dict]:
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"question": question},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        print("Request timeout (30s)")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
result = ask_sales_question("Total revenue by region last quarter?")
if result:
    print(result['answer'])
```

### Pandas Integration

```python
import requests
import pandas as pd

response = requests.post(
    "http://localhost:8000/chat",
    json={"question": "Sales by category last 30 days"}
)

result = response.json()

# Convert to DataFrame
df = pd.DataFrame(result['data_preview'])
print(df)
print(f"\nAnswer: {result['answer']}")
```

---

## JavaScript/Node.js Integration

### Fetch API

```javascript
const askQuestion = async (question) => {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Usage
askQuestion("What were total sales last month?")
  .then(result => {
    console.log('Answer:', result.answer);
    console.log('SQL:', result.generated_sql);
    console.log('Data:', result.data_preview);
  })
  .catch(error => console.error(error));
```

### Axios

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

const askQuestion = async (question) => {
  try {
    const { data } = await apiClient.post('/chat', { question });
    return data;
  } catch (error) {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
};

export default askQuestion;
```

### With Polling (Long Requests)

```javascript
const askQuestionWithPolling = async (question, maxRetries = 5) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        timeout: 30000,
      });

      if (response.ok) {
        return await response.json();
      }

      if (response.status === 500) {
        console.log(`Retry ${i + 1}/${maxRetries}...`);
        await new Promise(r => setTimeout(r, 2000)); // Wait 2s
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
};
```

---

## React Hook

```javascript
import { useState } from 'react';
import axios from 'axios';

export const useSalesChat = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const askQuestion = async (question) => {
    setLoading(true);
    setError(null);

    try {
      const { data } = await axios.post(
        'http://localhost:8000/chat',
        { question },
        { timeout: 30000 }
      );
      return data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message;
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { askQuestion, loading, error };
};

// Usage
function ChatComponent() {
  const { askQuestion, loading, error } = useSalesChat();

  const handleQuestion = async (q) => {
    const result = await askQuestion(q);
    console.log(result);
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={() => handleQuestion('Total sales last month?')}>
        Ask Question
      </button>
    </div>
  );
}
```

---

## cURL Commands

### Basic Query

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were total sales last month?"}'
```

### With Pretty JSON Output

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "Top 5 products by revenue"}' | jq '.'
```

### Save to File

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "Sales by region"}' > response.json
```

### With Timeout

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "..."}' \
  --max-time 30
```

---

## Webhook Integration

### Receiving Chat Results

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/sales-result")
async def receive_sales_result(request: Request):
    """Endpoint to receive chat results from chatbot."""
    payload = await request.json()
    
    result = {
        "question": payload["question"],
        "answer": payload["answer"],
        "sql": payload["generated_sql"],
        "rows": len(payload["data_preview"])
    }
    
    # Process result (save to DB, send email, etc.)
    print(f"Received: {result}")
    
    return {"status": "received"}
```

### Calling Webhook from Chatbot

```python
# In app/services/analytics_service.py, after processing:

import httpx

async def notify_webhook(result: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://your-system.com/webhook/sales-result",
            json=result,
            timeout=5
        )
```

---

## Streaming Responses (Optional Enhancement)

```python
from fastapi import StreamingResponse
import json

@app.post("/chat/stream")
async def chat_stream(payload: ChatRequest):
    """Stream response as it's generated."""
    
    async def generate():
        # Generate SQL
        sql = yield_sql_slowly()
        yield f'data: {json.dumps({"type": "sql", "value": sql})}\n\n'
        
        # Execute and stream rows
        for row in execute_and_yield_rows(sql):
            yield f'data: {json.dumps({"type": "row", "value": row})}\n\n'
        
        # Generate summary
        summary = yield_summary_slowly()
        yield f'data: {json.dumps({"type": "summary", "value": summary})}\n\n'
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

Frontend:

```javascript
const response = await fetch('http://localhost:8000/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ question: "..." })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = new TextDecoder().decode(value);
  const event = JSON.parse(text.slice(6)); // Remove "data: " prefix
  
  console.log(event); // {type: "sql", value: "SELECT ..."}
}
```

---

## Batch Processing

```python
import asyncio
from typing import List

async def batch_questions(questions: List[str]):
    tasks = [
        ask_question_async(q) for q in questions
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
results = await batch_questions([
    "Total sales last month?",
    "Top region by revenue?",
    "Average transaction value?"
])
```

---

## Caching Results

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_question(question: str):
    """Cache answers for repeated questions."""
    cache_key = hashlib.md5(question.encode()).hexdigest()
    
    # Check cache first
    cached = get_from_cache(cache_key)
    if cached:
        return cached
    
    # Make request
    result = ask_question(question)
    
    # Store in cache
    save_to_cache(cache_key, result)
    
    return result
```

---

## Monitoring & Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

request_count = Counter('chat_requests_total', 'Total requests')
request_duration = Histogram('chat_request_duration_seconds', 'Request duration')

@request_duration.time()
@app.post("/chat")
def chat(payload: ChatRequest):
    request_count.inc()
    # ... existing code
```

### OpenTelemetry Integration

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(...) # Configure your backend
)

tracer = trace.get_tracer(__name__)

@app.post("/chat")
def chat(payload: ChatRequest):
    with tracer.start_as_current_span("chat_request") as span:
        span.set_attribute("question", payload.question)
        # ... rest of code
```

---

## Testing Integration

```bash
# Test with pytest
pytest test_api.py -v

# Test with newman (Postman CLI)
newman run sales-analytics.postman_collection.json

# Test with k6 (load testing)
k6 run load_test.js \
  --vus 10 \
  --duration 30s
```

---

## Production Considerations

1. **Add API Key/JWT Auth**: Restrict access to authorized users
2. **Rate Limiting**: Limit requests per user/IP
3. **Caching**: Cache similar questions
4. **Logging**: Track all requests for audit
5. **Monitoring**: Alert on errors, slow responses
6. **CDN**: Cache API responses where appropriate
7. **Retry Logic**: Implement exponential backoff for transient failures
