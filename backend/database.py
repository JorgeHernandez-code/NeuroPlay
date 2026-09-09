import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# --- Database URL -----------------------------------------------------------
# By default the app runs on a local SQLite file so anyone can clone and run
# it with zero setup. Set DATABASE_URL to use another engine, e.g. Postgres:
#   DATABASE_URL=postgresql+psycopg://user:pass@host:5432/neuroplay
# or SQL Server (requires the extra "pyodbc" dependency, see requirements):
#   DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Optional: build a SQL Server URL from discrete env vars if they exist,
    # otherwise fall back to SQLite.
    server = os.getenv("SQLSERVER_SERVER")
    if server:
        user = os.getenv("SQLSERVER_USER", "sa")
        pwd = os.getenv("SQLSERVER_PASSWORD", "")
        db = os.getenv("SQLSERVER_DATABASE", "NeuroPlayDB")
        driver = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
        DATABASE_URL = (
            f"mssql+pyodbc://{user}:{quote_plus(pwd)}@{server}/{db}"
            f"?driver={quote_plus(driver)}&TrustServerCertificate=yes"
        )
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URL = f"sqlite:///{os.path.join(base_dir, 'neuroplay.db')}"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
