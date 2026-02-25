import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env.local')

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    sslmode=os.getenv('DB_SSL_MODE', 'require')
)

cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='olist_master_sales' ORDER BY ordinal_position")
print([r[0] for r in cur.fetchall()])

cur.execute("SELECT COUNT(*) FROM olist_master_sales")
print('row_count:', cur.fetchone()[0])

cur.execute("SELECT * FROM olist_master_sales LIMIT 1")
print('sample:', cur.fetchone())

conn.close()
