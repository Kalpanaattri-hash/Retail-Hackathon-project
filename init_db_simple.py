#!/usr/bin/env python
"""
Simple database initialization using raw SQL (no SQLAlchemy).
Creates tables and seeds sample data for testing.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def init_db() -> None:
    """Initialize SQLite database with schema and sample data."""
    
    # Connect to database
    db_path = Path(__file__).parent / "sales_analytics.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            segment TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            region TEXT NOT NULL,
            revenue REAL NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    print("✓ Tables created")
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] > 0:
        print("✓ Sample data already exists")
        conn.close()
        return
    
    print("Seeding sample data...")
    
    # Insert products
    products = [
        (1, "Laptop Pro", "Electronics"),
        (2, "Office Suite", "Software"),
        (3, "Monitor 27\"", "Electronics"),
        (4, "Keyboard Mechanical", "Accessories"),
        (5, "Mouse Wireless", "Accessories"),
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?)", products)
    print(f"✓ Inserted {len(products)} products")
    
    # Insert customers
    customers = [
        (1, "Acme Corp", "Enterprise"),
        (2, "StartUp Inc", "SMB"),
        (3, "Local Store", "Retail"),
        (4, "Global Retail", "Enterprise"),
        (5, "Tech Startup", "SMB"),
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?)", customers)
    print(f"✓ Inserted {len(customers)} customers")
    
    # Insert sales records
    sales = []
    base_date = datetime.now().date()
    regions = ["North", "South", "East", "West"]
    product_ids = [1, 2, 3, 4, 5]
    
    for i in range(200):
        sale_date = base_date - timedelta(days=i % 90)
        sales.append((
            i + 1,
            product_ids[i % len(product_ids)],
            regions[i % len(regions)],
            round(500 + (i * 17.3) % 5000, 2),
            (i % 20) + 1,
            str(sale_date)
        ))
    
    cursor.executemany(
        "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)",
        sales
    )
    print(f"✓ Inserted {len(sales)} sales records")
    
    conn.commit()
    conn.close()
    print("✓ Database seeding complete!")


if __name__ == "__main__":
    init_db()
