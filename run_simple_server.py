#!/usr/bin/env python3
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from wsgiref.simple_server import make_server


class ChatServer:
    def __init__(self):
        self.db_path = Path(__file__).parent / "sales_analytics.db"
        self.history = []
    
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        if path == '/health' and method == 'GET':
            return self.health(start_response)
        elif path == '/chat' and method == 'POST':
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length).decode()
            return self.chat(body, start_response)
        elif method == 'OPTIONS':
            return self.cors_preflight(start_response)
        else:
            return self.not_found(start_response)
    
    def health(self, start_response):
        response = {"status": "ok", "service": "Sales Analytics Chatbot"}
        text = json.dumps(response)
        start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
        return [text.encode()]
    
    def cors_preflight(self, start_response):
        start_response('204 No Content', [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type')
        ])
        return [b'']
    
    def chat(self, body, start_response):
        try:
            request = json.loads(body)
            question = request.get('question', '').strip()
            
            if not question:
                raise ValueError("Empty question")
            
            self.history.append({"role": "user", "content": question})
            answer, sql, data = self._process(question)
            self.history.append({"role": "assistant", "content": answer})
            
            response = {
                "answer": answer,
                "generated_sql": sql,
                "data_preview": data,
                "conversation_history": self.history[-10:]
            }
            
            text = json.dumps(response)
            start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [text.encode()]
        
        except Exception as e:
            response = {"error": str(e)}
            text = json.dumps(response)
            start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [text.encode()]
    
    def _process(self, question):
        q_lower = question.lower()
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if 'total' in q_lower and ('sales' in q_lower or 'revenue' in q_lower):
                sql = "SELECT SUM(revenue) as total, COUNT(*) as count FROM sales"
                cursor.execute(sql)
                row = dict(cursor.fetchone())
                total = row.get('total', 0) or 0
                count = row.get('count', 0) or 0
                answer = f"Total sales: ${total:,.2f} from {count} transactions"
                data = [row]
            
            elif 'region' in q_lower:
                sql = "SELECT region, SUM(revenue) as revenue, COUNT(*) as count FROM sales GROUP BY region ORDER BY revenue DESC"
                cursor.execute(sql)
                rows = [dict(r) for r in cursor.fetchall()]
                answer = "Sales by region: " + ", ".join([f"{r['region']}: ${r['revenue']:,.2f}" for r in rows])
                data = rows
            
            elif 'product' in q_lower and 'top' in q_lower:
                sql = "SELECT p.name, SUM(s.revenue) as revenue FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.name ORDER BY revenue DESC LIMIT 5"
                cursor.execute(sql)
                rows = [dict(r) for r in cursor.fetchall()]
                answer = "Top products: " + ", ".join([f"{r['name']}: ${r['revenue']:,.2f}" for r in rows])
                data = rows
            
            elif 'trend' in q_lower:
                sql = "SELECT sale_date, SUM(revenue) as revenue FROM sales GROUP BY sale_date ORDER BY sale_date DESC LIMIT 7"
                cursor.execute(sql)
                rows = [dict(r) for r in cursor.fetchall()]
                answer = f"Sales trend for last 7 days: {len(rows)} records"
                data = rows
            
            else:
                sql = "SELECT COUNT(*) as count, SUM(revenue) as total, AVG(revenue) as avg FROM sales"
                cursor.execute(sql)
                row = dict(cursor.fetchone())
                answer = f"Database summary: {row['count']} sales, ${row['total']:,.2f} total revenue"
                data = [row]
            
            conn.close()
            return answer, sql, data
        
        except Exception as e:
            return f"Error: {str(e)}", "", []
    
    def not_found(self, start_response):
        response = {"error": "Not found"}
        text = json.dumps(response)
        start_response('404 Not Found', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
        return [text.encode()]


if __name__ == "__main__":
    app = ChatServer()
    server = make_server('0.0.0.0', 8000, app)
    print("✓ Server started on http://0.0.0.0:8000")
    print("✓ Health: http://localhost:8000/health")
    print("✓ Chat: POST http://localhost:8000/chat")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
