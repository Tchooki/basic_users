from fastapi import FastAPI

from app.db.crud import create_tables

app = FastAPI()


@app.get("/")
def root():
    create_tables()
    return {"message": "Hello from basic-users!"}
