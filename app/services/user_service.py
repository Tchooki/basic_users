from sqlalchemy import text

from app.db.setup_db import get_connection


class UserService:
    def __init__(self):
        pass

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: str | None,
    ) -> None:
        with get_connection() as conn:
            conn.execute(
                text(
                    """
            INSERT INTO users (first_name, last_name, email, password, phone)
            VALUES (:first_name, :last_name, :email, :password, :phone)
            ON CONFLICT (email) DO NOTHING
            """
                ),
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": password,
                    "phone": phone,
                },
            )
