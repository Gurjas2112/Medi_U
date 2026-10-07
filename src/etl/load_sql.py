"""Step 3: load PascalCase Patients into SQLite or SQL Server and sync the analytics DB."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import (
    ANALYTICS_DB,
    CLEANED_FILE,
    CLEANED_SQLITE,
    SAMPLE_CSV,
    SAMPLE_ROW_LIMIT,
    TABLE_NAME,
    ensure_directories,
    sqlite_uri,
)
from src.schema import to_pascal_case


def get_engine():
    db_engine = os.getenv("DB_ENGINE", "sqlite").lower()
    if db_engine == "sqlserver":
        server = os.getenv("DB_SERVER", "localhost")
        database = os.getenv("DB_NAME", "HospitalDB")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server").replace(" ", "+")
        if username and password:
            conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
        else:
            conn_str = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"
        print(f"Connecting to SQL Server: {server}/{database}")
        return create_engine(conn_str)

    ensure_directories()
    print(f"Using local SQLite at: {CLEANED_SQLITE}")
    return create_engine(sqlite_uri(CLEANED_SQLITE))


def create_database_if_not_exists() -> None:
    if os.getenv("DB_ENGINE", "sqlite").lower() != "sqlserver":
        return

    server = os.getenv("DB_SERVER", "localhost")
    database = os.getenv("DB_NAME", "HospitalDB")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server").replace(" ", "+")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    master_conn_str = (
        f"mssql+pyodbc://{username}:{password}@{server}/master?driver={driver}"
        if username and password
        else f"mssql+pyodbc://@{server}/master?driver={driver}&trusted_connection=yes"
    )
    master_engine = create_engine(master_conn_str, isolation_level="AUTOCOMMIT")
    with master_engine.connect() as conn:
        conn.execute(
            text(
                f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{database}') "
                f"CREATE DATABASE [{database}]"
            )
        )
    print(f"Confirmed database '{database}' exists.")


def _write_sqlite(df: pd.DataFrame, path: Path) -> None:
    ensure_directories()
    if path.exists():
        path.unlink()
    engine = create_engine(sqlite_uri(path))
    df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)


def load_to_sql(df: pd.DataFrame):
    df = to_pascal_case(df)
    create_database_if_not_exists()
    engine = get_engine()
    df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into table '{TABLE_NAME}'.")

    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()
        print(f"Verification: {TABLE_NAME} now contains {count} rows.")

    sample = df.head(SAMPLE_ROW_LIMIT).copy()
    sample.to_csv(SAMPLE_CSV, index=False)
    _write_sqlite(sample, ANALYTICS_DB)
    print(f"Analytics SQLite synced: {ANALYTICS_DB} ({len(sample)} rows)")
    print(f"Hostable sample CSV written: {SAMPLE_CSV}")
    return engine


def main(cleaned_path: Path = CLEANED_FILE):
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Cleaned file not found at {cleaned_path}. Run transform first.")
    df = pd.read_csv(cleaned_path)
    return load_to_sql(df)


if __name__ == "__main__":
    main()
