#!/usr/bin/env python
"""Verify RDS database content and compare with SQLite."""

import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

# Load from .env.local explicitly
load_dotenv('.env.local')

print(f"🔍 Environment check:")
print(f"   DB_HOST: {os.getenv('DB_HOST')}")
print(f"   DB_USER: {os.getenv('DB_USER')}")
print(f"   DB_NAME: {os.getenv('DB_NAME')}")
print()

def get_rds_stats():
    """Get data stats from RDS."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            sslmode=os.getenv('DB_SSL_MODE', 'require')
        )
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) FROM sales;')
        sales_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products;')
        products_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customers;')
        customers_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(revenue) FROM sales;')
        total_revenue = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute('SELECT id, name FROM products LIMIT 3;')
        sample_products = cursor.fetchall()
        
        cursor.execute('SELECT region, COUNT(*) as count, SUM(revenue) as revenue FROM sales GROUP BY region ORDER BY revenue DESC;')
        sales_by_region = cursor.fetchall()
        
        conn.close()
        
        return {
            'sales_count': sales_count,
            'products_count': products_count,
            'customers_count': customers_count,
            'total_revenue': total_revenue,
            'sample_products': sample_products,
            'sales_by_region': sales_by_region,
            'status': '✅ RDS Connected'
        }
    except Exception as e:
        return {
            'status': f'❌ RDS Connection Failed: {e}'
        }

def get_sqlite_stats():
    """Get data stats from SQLite."""
    try:
        conn = sqlite3.connect('sales_analytics.db')
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute('SELECT COUNT(*) FROM sales;')
        sales_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products;')
        products_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customers;')
        customers_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(revenue) FROM sales;')
        total_revenue = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute('SELECT id, name FROM products LIMIT 3;')
        sample_products = cursor.fetchall()
        
        cursor.execute('SELECT region, COUNT(*) as count, SUM(revenue) as revenue FROM sales GROUP BY region ORDER BY revenue DESC;')
        sales_by_region = cursor.fetchall()
        
        conn.close()
        
        return {
            'sales_count': sales_count,
            'products_count': products_count,
            'customers_count': customers_count,
            'total_revenue': total_revenue,
            'sample_products': sample_products,
            'sales_by_region': sales_by_region,
            'status': '✅ SQLite Found'
        }
    except Exception as e:
        return {
            'status': f'❌ SQLite Error: {e}'
        }

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE VERIFICATION REPORT")
    print("=" * 80)
    
    # Check RDS
    print("\n📊 RDS DATABASE (PostgreSQL):")
    print("-" * 80)
    rds_stats = get_rds_stats()
    print(rds_stats['status'])
    if 'sales_count' in rds_stats:
        print(f"   Sales Records: {rds_stats['sales_count']}")
        print(f"   Products: {rds_stats['products_count']}")
        print(f"   Customers: {rds_stats['customers_count']}")
        print(f"   Total Revenue: ${rds_stats['total_revenue']:,.2f}" if rds_stats['total_revenue'] else "   Total Revenue: $0.00")
        print(f"\n   Sample Products: {rds_stats['sample_products']}")
        print(f"\n   Sales by Region:")
        for region, count, revenue in rds_stats['sales_by_region']:
            print(f"      {region}: {count} sales, ${revenue:,.2f}")
    
    # Check SQLite
    print("\n📊 SQLITE DATABASE (Local):")
    print("-" * 80)
    sqlite_stats = get_sqlite_stats()
    print(sqlite_stats['status'])
    if 'sales_count' in sqlite_stats:
        print(f"   Sales Records: {sqlite_stats['sales_count']}")
        print(f"   Products: {sqlite_stats['products_count']}")
        print(f"   Customers: {sqlite_stats['customers_count']}")
        print(f"   Total Revenue: ${sqlite_stats['total_revenue']:,.2f}" if sqlite_stats['total_revenue'] else "   Total Revenue: $0.00")
        print(f"\n   Sample Products: {sqlite_stats['sample_products']}")
        print(f"\n   Sales by Region:")
        for region, count, revenue in sqlite_stats['sales_by_region']:
            print(f"      {region}: {count} sales, ${revenue:,.2f}")
    
    # Comparison
    print("\n📈 COMPARISON:")
    print("-" * 80)
    if 'sales_count' in rds_stats and 'sales_count' in sqlite_stats:
        if rds_stats['sales_count'] == sqlite_stats['sales_count']:
            print("⚠️  Both databases have SAME data count")
            print("   → Cannot determine which one is being used!")
        else:
            print(f"📍 RDS: {rds_stats['sales_count']} records")
            print(f"📍 SQLite: {sqlite_stats['sales_count']} records")
            print(f"\n✅ Different counts! Easiest to verify which is being used:")
            print(f"   → Ask chatbot a question and check the answer")
            print(f"   → It should return: {rds_stats['sales_count'] if rds_stats['sales_count'] > sqlite_stats['sales_count'] else sqlite_stats['sales_count']} records")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print("1. Run: python run_simple_server.py")
    print("2. Ask: What are total sales?")
    print("3. Check if count matches RDS or SQLite above")
    print("=" * 80)
