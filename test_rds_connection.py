#!/usr/bin/env python
"""Test RDS connection and verify database setup."""

import psycopg2
import sys

try:
    print("Connecting to RDS...")
    conn = psycopg2.connect(
        host='sales-analytics.cuna0emog4au.us-east-1.rds.amazonaws.com',
        port=5432,
        database='postgres',
        user='sejal_sales',
        password='Sales_1234',
        sslmode='require',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    # Test connection
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print('\n✅ RDS Connection Successful!')
    print(f'PostgreSQL: {version[:80]}')
    
    # Check if tables exist
    cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema=\'public\'')
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    print(f'\nTables in RDS: {table_names}')
    
    # Check record counts
    if 'sales' in table_names:
        cursor.execute('SELECT COUNT(*) FROM sales;')
        sales_count = cursor.fetchone()[0]
        print(f'Sales records: {sales_count}')
    
    if 'products' in table_names:
        cursor.execute('SELECT COUNT(*) FROM products;')
        products_count = cursor.fetchone()[0]
        print(f'Products: {products_count}')
    
    if 'customers' in table_names:
        cursor.execute('SELECT COUNT(*) FROM customers;')
        customers_count = cursor.fetchone()[0]
        print(f'Customers: {customers_count}')
    
    conn.close()
    print('\n✅ All checks passed! RDS is ready.')
    
except Exception as e:
    print(f'\n❌ Connection Failed: {type(e).__name__}')
    print(f'Error: {e}')
    sys.exit(1)
