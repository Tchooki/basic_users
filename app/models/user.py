from pydantic import BaseModel


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str | None = None


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
