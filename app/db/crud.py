import datetime as dt
import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from psycopg2 import sql

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Utilisation d'un Engine SQLAlchemy pour le Connection Pooling (très important pour la perf)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)

@contextmanager
def get_connection():
    """Gestionnaire de contexte pour obtenir une connexion du pool."""
    conn = engine.raw_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def create_tables():
    """Initialise les tables de base et les premières partitions."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Table Users
            cursor.execute("""
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
            """)

            # Table Activities (Partitionnée)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id                  SERIAL PRIMARY KEY,
                user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                activity_type       VARCHAR(50) NOT NULL,
                activity_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) PARTITION BY RANGE (activity_date);
            """)
    
    # Créer les partitions pour le mois actuel et le suivant
    ensure_partitions()

def ensure_partitions():
    """Crée préemptivement les partitions pour le mois en cours et le suivant."""
    today = dt.date.today().replace(day=1)
    
    # On vérifie/crée pour les deux prochains mois (Aujourd'hui et M+1)
    for i in range(2):
        month_start = today + dt.timedelta(days=i*31) # Approximation safe pour replace
        month_start = month_start.replace(day=1)
        
        # Calcul de la fin du mois (le 1er du mois suivant)
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1, day=1)
            
        table_name = f"activities_{month_start.strftime('%Y_%m')}"
        
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Utilisation de psycopg2.sql pour sécuriser l'identifiant de table
                query = sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {table}
                    PARTITION OF activities
                    FOR VALUES FROM (%s) TO (%s);
                """).format(table=sql.Identifier(table_name))
                
                cursor.execute(query, (month_start, next_month))
