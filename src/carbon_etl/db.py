"""Database connection, built from settings in .env (never hard-coded)."""
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine


def get_engine():
    load_dotenv()
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],  # special characters are handled safely
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.environ["DB_NAME"],
    )
    return create_engine(url)