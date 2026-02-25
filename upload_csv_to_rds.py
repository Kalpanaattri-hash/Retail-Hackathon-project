#!/usr/bin/env python
"""Upload CSV data to RDS PostgreSQL."""

import os
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def upload_csv_to_rds() -> None:
    """Upload CSV data to RDS."""
    load_dotenv(".env.local")

    csv_path = r"c:\Users\Sejal Kumari\Downloads\olist_master_sales_df.csv"
    table_name = "olist_master_sales"

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if not all([db_host, db_port, db_name, db_user, db_password]):
        print("❌ Missing DB settings in .env.local")
        return

    try:
        print(f"📂 Loading CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        password_encoded = quote_plus(db_password)
        engine = create_engine(
            f"postgresql+psycopg2://{db_user}:{password_encoded}@{db_host}:{db_port}/{db_name}",
            pool_pre_ping=True,
        )

        print(f"📤 Uploading to RDS table: {table_name}")
        df.to_sql(table_name, engine, if_exists="replace", index=False, method="multi", chunksize=5000)

        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count.scalar_one()

        print(f"✅ Upload complete. Rows in {table_name}: {row_count}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    upload_csv_to_rds()
