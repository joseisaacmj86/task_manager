
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas
from app.database.database import SessionLocal

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Tasks(**task.dict(), status="PENDIENTE")  # Valor por defecto
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[schemas.Task], status_code=status.HTTP_200_OK)
async def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Tasks).all()

@router.get("/{task_id}", response_model=schemas.Task, status_code=status.HTTP_200_OK)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

@router.put("/{task_id}", response_model=schemas.Task, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/complete/{task_id}", response_model=schemas.Task, status_code=status.HTTP_200_OK)
async def toggle_task_status(task_id: int, status: str, db: Session = Depends(get_db)):
    db_task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task


# @router.put("/complete/{task_id}", response_model=schemas.Task, status_code=status.HTTP_200_OK)
# async def mark_task_as_completed(task_id: int, db: Session = Depends(get_db)):
#     db_task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
#     if db_task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
#     db_task.status = 'TERMINADA'
#     db.commit()
#     db.refresh(db_task)
#     return db_task

