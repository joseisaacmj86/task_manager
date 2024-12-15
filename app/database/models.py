
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class Tasks(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.now(), index=True)  # Fecha automática   
    title = Column(String(255), index=True)
    description = Column(String(255))
    status = Column(String(255), index=True, default="PENDIENTE")  # Valor por defecto
