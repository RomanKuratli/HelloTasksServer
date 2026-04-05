from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TodoList(Base):
    __tablename__ = "todo_list"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    todo_tasks = relationship("TodoTask", back_populates="todo_list", cascade="all, delete")

class TodoTask(Base):
    __tablename__ = "todo_task"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(50), nullable=False)
    is_done = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)
    todo_list_id = Column(Integer, ForeignKey("todo_list.id"), nullable=False)
    todo_list = relationship("TodoList", back_populates="todo_tasks")