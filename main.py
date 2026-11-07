import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List

# Загружаем переменные из .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не найден. Создай файл .env")

# Создаем движок базы данных
engine = create_engine(DATABASE_URL, echo=False)

# Функция для создания таблиц
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Инициализация приложения
app = FastAPI(
    title="Automation Tasks API",
    description="API для управления личными скриптами",
    version="1.0.0"
)

# Создаем таблицы при запуске
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Модель данных (таблица в БД)
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    command: str
    is_active: bool = Field(default=True)
    last_run: str | None = Field(default=None)

# Зависимость для сессии БД
def get_session():
    with Session(engine) as session:
        yield session

# Эндпоинты

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API с PostgreSQL!"}

@app.post("/tasks/", response_model=Task, status_code=201)
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/", response_model=List[Task])
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    session.delete(task)
    session.commit()
    return {"message": "Задача удалена"}
#Made by https://github.com/Serega210810