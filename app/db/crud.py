import datetime as dt
import logging
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)


logger = logging.getLogger(__name__)


@contextmanager
def get_connection():
    """Context manager to get a SQLAlchemy connection from the pool."""
    with engine.connect() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Database error occurred")
            raise


def create_tables() -> None:
    """Initialise les tables de base et les premières partitions."""
    with get_connection() as conn:
        logger.info(
            "Vérification et création des tables de base (users, activities)..."
        )
        # Users
        conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS users (
                id              SERIAL PRIMARY KEY,
                first_name      VARCHAR(50) NOT NULL,
                last_name       VARCHAR(50) NOT NULL,
                email           VARCHAR(100) UNIQUE NOT NULL,
                password        VARCHAR(100) NOT NULL,
                phone           VARCHAR(20),
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """),
        )
        logger.info("Table 'users' vérifiée/créée.")

        # Activities (Partitioned)
        conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS activities (
                id                  SERIAL,
                user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                activity_type       VARCHAR(50) NOT NULL,
                activity_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) PARTITION BY RANGE (activity_date);
        """)
        )
        logger.info("Table 'activities' (partitionnée) vérifiée/créée.")

    # Créer les partitions pour le mois actuel et le suivant
    ensure_partitions()


def ensure_partitions() -> None:
    """Crée préemptivement les partitions pour le mois en cours et le suivant."""
    today = dt.date.today().replace(day=1)

    # Check for the current month and the next month
    for i in range(2):
        month_start = (today + dt.timedelta(days=i * 32)).replace(day=1)
        next_month = (month_start + dt.timedelta(days=32)).replace(day=1)

        table_name = f"activities_{month_start.strftime('%Y_%m')}"

        with get_connection() as conn:
            conn.execute(
                text(f"""
                    CREATE TABLE IF NOT EXISTS {table_name}
                    PARTITION OF activities
                    FOR VALUES FROM (:start) TO (:end);
                """),
                {"start": month_start, "end": next_month},
            )
            logger.info("Partition '%s' vérifiée/créée.", table_name)
