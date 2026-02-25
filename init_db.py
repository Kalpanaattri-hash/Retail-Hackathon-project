#!/usr/bin/env python
"""
Database initialization script.
Creates tables and seeds minimal sample data for testing.
"""

import os
from datetime import datetime, timedelta

from sqlalchemy import insert

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Product, Sale, Customer


def init_db() -> None:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

    db = SessionLocal()
    try:
        # Check if data exists
        if db.query(Product).first():
            print("✓ Sample data already exists")
            return

        print("Seeding sample data...")

        # Products
        products_data = [
            {"id": 1, "name": "Laptop Pro", "category": "Electronics"},
            {"id": 2, "name": "Office Suite", "category": "Software"},
            {"id": 3, "name": "Monitor 27\"", "category": "Electronics"},
            {"id": 4, "name": "Keyboard Mechanical", "category": "Accessories"},
            {"id": 5, "name": "Mouse Wireless", "category": "Accessories"},
        ]
        db.execute(insert(Product), products_data)
        print(f"✓ Inserted {len(products_data)} products")

        # Customers
        customers_data = [
            {"id": 1, "name": "Acme Corp", "segment": "Enterprise"},
            {"id": 2, "name": "StartUp Inc", "segment": "SMB"},
            {"id": 3, "name": "Local Store", "segment": "Retail"},
            {"id": 4, "name": "Global Retail", "segment": "Enterprise"},
            {"id": 5, "name": "Tech Startup", "segment": "SMB"},
        ]
        db.execute(insert(Customer), customers_data)
        print(f"✓ Inserted {len(customers_data)} customers")

        # Sales (generated for last 90 days)
        sales_data = []
        base_date = datetime.now().date()
        regions = ["North", "South", "East", "West"]
        products_ids = [1, 2, 3, 4, 5]

        for i in range(200):
            sale_date = base_date - timedelta(days=i % 90)
            sales_data.append(
                {
                    "id": i + 1,
                    "product_id": products_ids[i % len(products_ids)],
                    "region": regions[i % len(regions)],
                    "revenue": round(500 + (i * 17.3) % 5000, 2),
                    "quantity": (i % 20) + 1,
                    "sale_date": sale_date,
                }
            )

        db.execute(insert(Sale), sales_data)
        print(f"✓ Inserted {len(sales_data)} sales records")

        db.commit()
        print("✓ Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"✗ Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
