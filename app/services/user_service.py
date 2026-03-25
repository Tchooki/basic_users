import bcrypt
from sqlalchemy import text

from app.db.setup_db import get_connection


class UserService:
    def __init__(self):
        pass

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: str | None,
    ) -> dict | None:
        with get_connection() as conn:
            result = conn.execute(
                text("""
            INSERT INTO users (first_name, last_name, email, password, phone)
            VALUES (:first_name, :last_name, :email, :password, :phone)
            ON CONFLICT (email) DO NOTHING
            RETURNING id, first_name, last_name, email, phone
            """),
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": self.hash_password(password),
                    "phone": phone,
                },
            )
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None
