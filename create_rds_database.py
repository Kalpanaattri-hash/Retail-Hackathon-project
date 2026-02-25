import os

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


def main() -> None:
    load_dotenv('.env.local')

    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', '5432'))
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_ssl_mode = os.getenv('DB_SSL_MODE', 'require')

    if not all([db_host, db_name, db_user, db_password]):
        raise RuntimeError('Missing DB settings in .env.local')

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database='postgres',
        user=db_user,
        password=db_password,
        sslmode=db_ssl_mode,
        connect_timeout=15,
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
    exists = cur.fetchone() is not None

    if exists:
        print(f"Database already exists: {db_name}")
    else:
        cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
        print(f"Database created: {db_name}")

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
