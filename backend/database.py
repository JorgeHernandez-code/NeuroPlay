import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

SERVER = os.getenv("SQLSERVER_SERVER")
DB = os.getenv("SQLSERVER_DATABASE")
USER = os.getenv("SQLSERVER_USER")
PWD = os.getenv("SQLSERVER_PASSWORD")
DRIVER = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

# mssql+pyodbc connection string
conn_str = (
    f"mssql+pyodbc://{USER}:{quote_plus(PWD)}@{SERVER}/{DB}"
    f"?driver={quote_plus(DRIVER)}&TrustServerCertificate=yes"
)

engine = create_engine(conn_str, pool_pre_ping=True, fast_executemany=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
