from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# ==== todo_task ====

class TaskBase(BaseModel):
    description: str
    is_done: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime
    todo_list_id: int

class TaskUpdate(TaskBase):
    description: Optional[str] = None
    is_done: Optional[bool] = None

# ==== todo_list ====

class TodoListBase(BaseModel):
    title: str

class TodoListCreate(TodoListBase):
    pass

class TodoListUpdate(TodoListBase):
    pass

class TodoList(TodoListBase):
    id: int
    todo_tasks: list[Task] = []

    model_config = ConfigDict(from_attributes=True)

