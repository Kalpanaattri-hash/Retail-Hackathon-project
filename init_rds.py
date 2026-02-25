#!/usr/bin/env python
"""Initialize RDS PostgreSQL database with sample data."""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env.local explicitly
load_dotenv('.env.local')

def init_rds():
    """Initialize RDS PostgreSQL database with schema and sample data."""
    
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_name = os.getenv('DB_NAME', 'salesdb')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_ssl_mode = os.getenv('DB_SSL_MODE', 'require')
    
    if not db_host or not db_password:
        print("❌ RDS credentials not configured in .env.local")
        print(f"   DB_HOST: {db_host}")
        print(f"   DB_PASSWORD: {db_password}")
        print("Please set DB_HOST, DB_USER, DB_PASSWORD, etc.")
        return
    
    try:
        print(f"Connecting to RDS master database: {db_host}...")
        # First connect to master 'postgres' database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database='postgres',  # Connect to master database first
            user=db_user,
            password=db_password,
            sslmode=db_ssl_mode,
            connect_timeout=10
        )
        cursor = conn.cursor()
        conn.autocommit = True  # Need this to create database
        print("✓ Connected to RDS master database!")
        
        # Create database if it doesn't exist
        print(f"\nCreating database: {db_name}...")
        try:
            cursor.execute(f"CREATE DATABASE \"{db_name}\";")
            print(f"✓ Database '{db_name}' created")
        except psycopg2.Error as e:
            if 'already exists' in str(e):
                print(f"✓ Database '{db_name}' already exists")
            else:
                raise
        
        conn.close()
        
        # Now connect to the actual database
        print(f"Connecting to database: {db_name}...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            sslmode=db_ssl_mode,
            connect_timeout=10
        )
        cursor = conn.cursor()
        print("✓ Connected to database!")
        
        # Create tables
        print("\nCreating tables...")
        
        cursor.execute("""
            DROP TABLE IF EXISTS sales CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS customers CASCADE;
        """)
        
        cursor.execute("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL
            );
        """)
        print("✓ Created products table")
        
        cursor.execute("""
            CREATE TABLE customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                segment VARCHAR(50) NOT NULL
            );
        """)
        print("✓ Created customers table")
        
        cursor.execute("""
            CREATE TABLE sales (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id),
                customer_id INTEGER,
                region VARCHAR(50) NOT NULL,
                revenue DECIMAL(10, 2) NOT NULL,
                quantity INTEGER NOT NULL,
                sale_date DATE NOT NULL
            );
        """)
        print("✓ Created sales table")
        
        # Insert products
        print("\nInserting sample data...")
        products = [
            ('Laptop', 'Electronics'),
            ('Monitor', 'Electronics'),
            ('Mouse', 'Accessories'),
            ('Keyboard', 'Accessories'),
            ('Headphones', 'Electronics'),
        ]
        
        for name, category in products:
            cursor.execute('INSERT INTO products (name, category) VALUES (%s, %s)', (name, category))
        print(f"✓ Inserted {len(products)} products")
        
        # Insert customers
        customers = [
            ('John Smith', 'Enterprise'),
            ('Sarah Johnson', 'SMB'),
            ('Mike Davis', 'Enterprise'),
            ('Emily Wilson', 'Startup'),
            ('David Brown', 'SMB'),
        ]
        
        for name, segment in customers:
            cursor.execute('INSERT INTO customers (name, segment) VALUES (%s, %s)', (name, segment))
        print(f"✓ Inserted {len(customers)} customers")
        
        # Insert sales data (200 records)
        regions = ['North', 'South', 'East', 'West']
        products_list = [(i+1, products[i][0]) for i in range(len(products))]
        base_date = datetime.now() - timedelta(days=90)
        
        sales_count = 0
        for day in range(90):
            sale_date = base_date + timedelta(days=day)
            for _ in range(int(200/90)):  # ~2.22 per day
                product_id = (sales_count % len(products_list)) + 1
                region = regions[sales_count % len(regions)]
                revenue = round(100 + (sales_count % 900), 2)
                quantity = (sales_count % 5) + 1
                
                cursor.execute(
                    'INSERT INTO sales (product_id, customer_id, region, revenue, quantity, sale_date) VALUES (%s, %s, %s, %s, %s, %s)',
                    (product_id, (sales_count % 5) + 1, region, revenue, quantity, sale_date.date())
                )
                sales_count += 1
        
        print(f"✓ Inserted {sales_count} sales records")
        
        # Verify data
        cursor.execute('SELECT COUNT(*) FROM products;')
        products_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customers;')
        customers_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sales;')
        sales_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(revenue) FROM sales;')
        total_revenue = cursor.fetchone()[0]
        
        # Commit
        conn.commit()
        conn.close()
        
        print(f"\n✅ RDS Database initialized successfully!")
        print(f"   Products: {products_count}")
        print(f"   Customers: {customers_count}")
        print(f"   Sales: {sales_count}")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return

if __name__ == "__main__":
    init_rds()
