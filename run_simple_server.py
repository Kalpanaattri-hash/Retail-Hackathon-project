#!/usr/bin/env python3
import base64
import io
import json
import os
from wsgiref.simple_server import make_server
from dotenv import load_dotenv
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.use('Agg')

# Load environment variables
load_dotenv('.env.local')

class ChatServer:
    def __init__(self):
        # RDS-only configuration
        self.db_host = os.getenv('DB_HOST')
        self.db_port = int(os.getenv('DB_PORT', 5432))
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_ssl_mode = os.getenv('DB_SSL_MODE', 'require')
        self.table_name = 'olist_master_sales'
        self.history = []

        if not all([self.db_host, self.db_name, self.db_user, self.db_password]):
            raise RuntimeError("RDS settings missing in .env.local. This server is configured for RDS only.")

        print(f"✓ Using PostgreSQL (RDS): {self.db_host}/{self.db_name}")
        print(f"✓ Using table: {self.table_name}")
    
    def get_connection(self):
        """Get PostgreSQL connection."""
        import psycopg2
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            sslmode=self.db_ssl_mode,
            connect_timeout=10
        )
    
    def dict_from_cursor(self, cursor, fetchone=False):
        """Convert PostgreSQL cursor results to dictionaries."""
        col_names = [desc[0] for desc in cursor.description]
        if fetchone:
            row = cursor.fetchone()
            return dict(zip(col_names, row)) if row else None
        else:
            rows = cursor.fetchall()
            return [dict(zip(col_names, row)) for row in rows]
    
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        if path == '/health' and method == 'GET':
            return self.health(start_response)
        elif path == '/chat' and method == 'POST':
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length).decode()
            return self.chat(body, start_response)
        elif path == '/dashboard/options' and method == 'GET':
            return self.dashboard_options(start_response)
        elif path == '/dashboard/charts' and method == 'POST':
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length).decode()
            return self.dashboard_charts(body, start_response)
        elif method == 'OPTIONS':
            return self.cors_preflight(start_response)
        else:
            return self.not_found(start_response)
    
    def health(self, start_response):
        response = {
            "status": "ok",
            "service": "Sales Analytics Chatbot",
            "database": "RDS PostgreSQL",
            "table": self.table_name,
        }
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

    def dashboard_options(self, start_response):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(f"SELECT DISTINCT customer_gender FROM {self.table_name} WHERE customer_gender IS NOT NULL ORDER BY customer_gender")
            customer_genders = [row[0] for row in cursor.fetchall() if row[0]]

            cursor.execute(f"SELECT DISTINCT customer_state FROM {self.table_name} WHERE customer_state IS NOT NULL ORDER BY customer_state")
            customer_states = [row[0] for row in cursor.fetchall() if row[0]]

            cursor.execute(f"SELECT DISTINCT product_category_name FROM {self.table_name} WHERE product_category_name IS NOT NULL ORDER BY product_category_name")
            product_categories = [row[0] for row in cursor.fetchall() if row[0]]

            conn.close()

            response = {
                "customer_genders": customer_genders,
                "customer_states": customer_states,
                "product_categories": product_categories,
            }
            text = json.dumps(response)
            start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [text.encode()]
        except Exception as e:
            response = {"error": str(e)}
            text = json.dumps(response)
            start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [text.encode()]

    def dashboard_charts(self, body, start_response):
        try:
            payload = json.loads(body or '{}')
            customer_genders = payload.get('customer_genders', [])
            customer_states = payload.get('customer_states', [])
            product_categories = payload.get('product_categories', [])
            selected_dimensions = payload.get('selected_dimensions', ['customer_gender', 'customer_state', 'product_category_name'])
            measure = payload.get('measure', 'sales_value')
            measure_column = 'order_sale_value' if measure == 'sales_value' else 'order_items_qty'

            conditions = []
            params = []

            if customer_genders:
                placeholders = ','.join(['%s'] * len(customer_genders))
                conditions.append(f"customer_gender IN ({placeholders})")
                params.extend(customer_genders)

            if customer_states:
                placeholders = ','.join(['%s'] * len(customer_states))
                conditions.append(f"customer_state IN ({placeholders})")
                params.extend(customer_states)

            if product_categories:
                placeholders = ','.join(['%s'] * len(product_categories))
                conditions.append(f"product_category_name IN ({placeholders})")
                params.extend(product_categories)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''

            labels_map = {
                'customer_gender': 'Customer Gender',
                'customer_state': 'Customer State',
                'product_category_name': 'Product Category',
            }

            conn = self.get_connection()
            cursor = conn.cursor()
            charts = []

            sns.set_theme(style='whitegrid')

            for dimension in selected_dimensions:
                if dimension not in labels_map:
                    continue

                query = f"""
                    SELECT {dimension} AS label, SUM({measure_column}) AS metric
                    FROM {self.table_name}
                    {where_clause}
                    {'AND' if where_clause else 'WHERE'} {dimension} IS NOT NULL
                    GROUP BY {dimension}
                    ORDER BY metric DESC
                    LIMIT 12
                """

                cursor.execute(query, params)
                rows = cursor.fetchall()
                if not rows:
                    continue

                labels = [str(r[0]) for r in rows]
                values = [float(r[1]) for r in rows]

                fig, ax = plt.subplots(figsize=(8, 4.5))
                sns.barplot(x=labels, y=values, ax=ax, color='#2563eb')
                metric_label = 'Sales Value' if measure == 'sales_value' else 'Sales Quantity'
                ax.set_title(f"{labels_map[dimension]} by {metric_label}")
                ax.set_xlabel(labels_map[dimension])
                ax.set_ylabel(metric_label)
                ax.tick_params(axis='x', rotation=30)
                fig.tight_layout()

                buffer = io.BytesIO()
                fig.savefig(buffer, format='png', dpi=120)
                plt.close(fig)
                buffer.seek(0)

                charts.append({
                    'dimension': dimension,
                    'title': ax.get_title(),
                    'image_base64': base64.b64encode(buffer.read()).decode('utf-8')
                })

            conn.close()

            response = {
                'measure': measure,
                'charts': charts
            }
            text = json.dumps(response)
            start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [text.encode()]
        except Exception as e:
            response = {"error": str(e)}
            text = json.dumps(response)
            start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [text.encode()]
    
    def _process(self, question):
        q_lower = question.lower()
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if 'total' in q_lower and ('sales' in q_lower or 'revenue' in q_lower):
                sql = f"SELECT SUM(order_sale_value) as total, COUNT(*) as count FROM {self.table_name}"
                cursor.execute(sql)
                row = self.dict_from_cursor(cursor, fetchone=True)
                total = row.get('total', 0) or 0
                count = row.get('count', 0) or 0
                answer = f"Total sales: ${total:,.2f} from {count} transactions"
                data = [row]
            
            elif 'region' in q_lower:
                sql = f"SELECT customer_state as region, SUM(order_sale_value) as revenue, COUNT(*) as count FROM {self.table_name} GROUP BY customer_state ORDER BY revenue DESC LIMIT 10"
                cursor.execute(sql)
                rows = self.dict_from_cursor(cursor)
                answer = "Sales by region: " + ", ".join([f"{r['region']}: ${r['revenue']:,.2f}" for r in rows])
                data = rows
            
            elif 'product' in q_lower and 'top' in q_lower:
                sql = f"SELECT product_category_name as name, SUM(order_sale_value) as revenue FROM {self.table_name} GROUP BY product_category_name ORDER BY revenue DESC LIMIT 5"
                cursor.execute(sql)
                rows = self.dict_from_cursor(cursor)
                answer = "Top products: " + ", ".join([f"{r['name']}: ${r['revenue']:,.2f}" for r in rows])
                data = rows
            
            elif 'trend' in q_lower:
                sql = f"SELECT order_date, SUM(order_sale_value) as revenue FROM {self.table_name} GROUP BY order_date ORDER BY order_date DESC LIMIT 7"
                cursor.execute(sql)
                rows = self.dict_from_cursor(cursor)
                answer = f"Sales trend for last 7 days: {len(rows)} records"
                data = rows
            
            else:
                sql = f"SELECT COUNT(*) as count, SUM(order_sale_value) as total, AVG(order_sale_value) as avg FROM {self.table_name}"
                cursor.execute(sql)
                row = self.dict_from_cursor(cursor, fetchone=True)
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
