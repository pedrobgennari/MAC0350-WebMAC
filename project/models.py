from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import date

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    password: str

    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    name: str
    description: str
    date: date

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tasks")