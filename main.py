from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from typing import List
import models, schemas
from database import engine, SessionLocal, get_db
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

TITLE = "HelloTasksServer"

app = FastAPI(title=TITLE)
app.add_middleware(
    CORSMiddleware,
    # Accept all ports from localhost/127.0.0.1
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==== ROUTES ====

@app.get("/")
def read_root():
    return {"message": f"{TITLE} is running"}

@app.get("/api/info")
def get_info():
    return {
        "status": "active",
        "stack": ["FastAPI", "SQLAlchemy", "PostgreSQL"]
    }

# ==== /api/todolists ====

def _get_list_or_404(list_id: int, db: Session) -> schemas.TodoList:
    todo_list = db.query(models.TodoList) \
        .filter(models.TodoList.id == list_id) \
        .first()
    
    if not todo_list:
        raise HTTPException(status_code=404, detail=f"TodoList with id {list_id} not found")
    
    return todo_list

@app.get("/api/todolists", response_model=list[schemas.TodoList])
def get_all_lists(db: Session = Depends(get_db)):
    return db.query(models.TodoList).all()

@app.get("/api/todolists/{list_id}", response_model=schemas.TodoList)
def get_list_by_id(list_id: int, db: Session=Depends(get_db)):
    return _get_list_or_404(list_id, db)

@app.post("/api/todolists", 
          response_model=schemas.TodoList, 
          status_code=status.HTTP_201_CREATED)
def create_list(todo_list: schemas.TodoListCreate, db: Session = Depends(get_db)):
    db_list = models.TodoList(title=todo_list.title)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

@app.delete("/api/todolists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(list_id: int, db: Session = Depends(get_db)):
    todo_list = _get_list_or_404(list_id, db)   
    db.delete(todo_list)
    db.commit()
    return None

@app.patch("/api/todolists/{list_id}", response_model=schemas.TodoList)
def update_task(
    list_id: int, 
    list_update: schemas.TodoListUpdate,
    db: Session = Depends(get_db)):

    db_list = _get_task_or_404(list_id, db)
    update_data = list_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_list, key, value)
    
    db.commit()
    db.refresh(db_list)
    return db_list
# ==== /api/todotasks ====    

def _get_task_or_404(task_id: int, db: Session) -> schemas.Task:
    todo_task = db.query(models.TodoTask) \
        .filter(models.TodoTask.id == task_id) \
        .first()
    
    if not todo_task:
        raise HTTPException(status_code=404, detail=f"TodoList with id {task_id} not found")
    
    return todo_task


@app.get("/api/todotasks/{task_id}", response_model=schemas.Task)
def get_list_by_id(task_id: int, db: Session=Depends(get_db)):
    return _get_task_or_404(task_id, db)
    

@app.post("/api/todolists/{list_id}/tasks", 
          response_model=schemas.Task, 
          status_code=status.HTTP_201_CREATED)
def create_task(list_id: int, todo_task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.TodoTask(
        todo_list_id=list_id,
        description=todo_task.description,
        is_done=todo_task.is_done,
        created_at = datetime.now()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/api/todotasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = _get_task_or_404(task_id, db)
    db.delete(db_task)
    db.commit()
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

@app.patch("/api/todotasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int, 
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db)):

    db_task = _get_task_or_404(task_id, db)
    update_data = task_update.model_dump(exclude_unset=True)
    print(f"{update_data=}")
    for key, value in update_data.items():
        print(f"Task {db_task.id=} {db_task.description=}: {key} => {value}")
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task