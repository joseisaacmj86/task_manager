from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.database import models, schemas
from app.database.database import SessionLocal
from fastapi.responses import FileResponse, JSONResponse
import json
import tempfile
import os


router = APIRouter(
    prefix="/action",
    tags=["action"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/export", status_code=status.HTTP_200_OK)
async def export_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Tasks).all()  # Obtener todas las tareas de la base de datos
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    
    tasks_data = [
        {
            "task_id": task.task_id,
            "date": task.date.isoformat() if task.date else None,
            "title": task.title,
            "description": task.description,
            "status": task.status
        }
        for task in tasks
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as temp_file:
        json.dump(tasks_data, temp_file, ensure_ascii=False, indent=4)
        temp_file_path = temp_file.name
    
    return FileResponse(
        path=temp_file_path,
        filename="exported_tasks.json",
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="exported_tasks.json"'}
    )


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_tasks(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un JSON")

    try:
        file_content = await file.read()
        tasks_data = json.loads(file_content)

        if not isinstance(tasks_data, list):
            raise HTTPException(status_code=400, detail="El contenido del archivo no es una lista válida")

        new_tasks = []
        for task in tasks_data:
            if not all(k in task for k in ("task_id", "date", "title", "description", "status")):
                continue

            existing_task = db.query(models.Tasks).filter_by(task_id=task["task_id"]).first()
            if not existing_task:
                new_task = models.Tasks(
                    task_id=task["task_id"],
                    date=task["date"],
                    title=task["title"],
                    description=task["description"],
                    status=task["status"]
                )
                new_tasks.append(new_task)

        if new_tasks:
            db.add_all(new_tasks)
            db.commit()

        return {
            "message": "Importación completada",
            "imported_tasks": len(new_tasks),
            "skipped_tasks": len(tasks_data) - len(new_tasks)
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El archivo JSON no es válido")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al importar tareas: {str(e)}")
