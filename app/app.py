from fastapi import FastAPI

from app.api.v1.users import users_router
from app.core.logging import setup_logging
from app.db.setup_db import create_tables

setup_logging()
app = FastAPI()

app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/")
def root():
    create_tables()
    return {"message": "Hello from basic-users!"}
