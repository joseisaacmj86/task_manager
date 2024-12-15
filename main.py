
# uvicorn main:app --reload

from fastapi import FastAPI, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from routers import export_import, tasks
from app.database.database import engine, SessionLocal
import app.database.models as models
import uvicorn
from starlette.requests import Request


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="API para gestionar tareas.",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configurar Jinja2
templates = Jinja2Templates(directory="app/templates")

# Configurar rutas estáticas para archivos CSS, JS e imagenes
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(tasks.router)
app.include_router(export_import.router)

# Ruta principal (home) para mostrar todas las tareas
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), page: int = Query(1), per_page: int = Query(5)):
    offset = (page - 1) * per_page
    tasks = db.query(models.Tasks).offset(offset).limit(per_page).all()
    total_tasks = db.query(models.Tasks).count()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tasks": tasks,
        "page": page,
        "total_pages": (total_tasks + per_page - 1) // per_page
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
