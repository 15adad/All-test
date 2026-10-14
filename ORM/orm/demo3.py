import decimal
from datetime import datetime
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, DateTime, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.testing.schema import mapped_column
from streamlit import status
from tomlkit import comment


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now, default=os.times(),
                                                  comment="创建时间默认当前系统时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, update_default=func.now, default=os.times())
    pass


engine = create_engine(
    "sqlite:///todo.db",
    connect_args={"check_same_thread": False},  # SQLite 多线程需要
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)


Base.metadata.create_all(engine)  # 自动建表


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
        finally:
            await session.close()


class TodoIn(BaseModel):  # 创建时客户端传的
    title: str


class TodoUpdate(BaseModel):  # 更新时传的，字段都可选
    title: str | None = None
    done: bool | None = None


class TodoOut(BaseModel):  # 返回给客户端的
    id: int
    title: str
    done: bool
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象读属性


app = FastAPI()


# 创建
@app.post("/todos", response_model=TodoOut)
def create_todo(data: TodoIn, db: Session = Depends(get_db)):
    todo = Todo(title=data.title)
    db.add(todo)
    db.commit()
    db.refresh(todo)  # 拿数据库生成的 id
    return todo

# 查所有
@app.get("/todos/todos_all", response_model=TodoOut)
async def get_all_todos(db: Session = Depends(get_db)):
    result = db.execute(select(Todo))
    return result.scalars().all()
# 查单个
@app.get("/todos/{todo_id}", response_model=TodoOut)
def select_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return todo


# 更新
@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    todo = select_todo(todo_id, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo
