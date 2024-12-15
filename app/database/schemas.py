from pydantic import BaseModel
from datetime import datetime


# Schemas tasks
class TaskCreate(BaseModel):
    title: str
    description: str

class Task(TaskCreate):
    task_id: int
    date: datetime 
    status: str

    class Config:
        from_attributes  = True  # Permite que los objetos de SQLAlchemy sean convertidos a este esquema

