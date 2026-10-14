from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]

class UserIn(BaseModel):
    name: str
    age: int

class UserOut(UserIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

engine = create_engine(
    "sqlite:///demo.db",
    connect_args={"check_same_thread": False}
)
Base.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

app = FastAPI()

@app.post("/users", response_model=UserOut)
def create_user(data: UserIn, db: Session = Depends(get_db)):
    user = User(name=data.name, age=data.age)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User)).all()