from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session
)

# ---------- 1. 定义模型（映射到数据库表） ----------
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int]

    # 一对多：一个用户有多篇文章
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.id} {self.name} ({self.age})>"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # 多对一：每篇文章属于一个用户
    author: Mapped["User"] = relationship(back_populates="posts")

    def __repr__(self):
        return f"<Post {self.id} {self.title}>"

# ---------- 2. 连接数据库并建表 ----------
engine = create_engine("sqlite:///demo.db", echo=False)
Base.metadata.create_all(engine)

# ---------- 3. 增（Create） ----------
with Session(engine) as session:
    alice = User(name="Alice", age=30)
    alice.posts = [Post(title="Hello ORM"), Post(title="SQLAlchemy 入门")]
    bob = User(name="Bob", age=25)
    bob.posts.append(Post(title="Bob 的第一篇文章"))

    session.add_all([alice, bob])
    session.commit()

# ---------- 4. 查（Read） ----------
with Session(engine) as session:
    # 查询所有用户
    users = session.scalars(select(User)).all()
    print("所有用户:", users)

    # 条件查询：年龄大于 26
    older = session.scalars(select(User).where(User.age > 26)).all()
    print("年龄 > 26:", older)

    # 通过关系导航（无需手写 JOIN）
    alice = session.scalars(select(User).where(User.name == "Alice")).first()
    print("Alice 的文章:", alice.posts)

    # 反向导航：从文章找作者
    post = session.scalars(select(Post).where(Post.title == "Hello ORM")).first()
    print("文章作者:", post.author)

# ---------- 5. 改（Update） ----------
with Session(engine) as session:
    # user = session.scalars(select(User).where(User.name == "Bob")).first()
    user = session.get(User.name,"Bob")
    user.age = 26          # 直接修改对象属性
    session.commit()
    print("Bob 更新后:", user)

# ---------- 6. 删（Delete） ----------
with Session(engine) as session:
    user = session.scalars(select(User).where(User.name == "Bob")).first()
    session.delete(user)   # 级联删除它的 posts
    session.commit()
    print("剩余用户:", session.scalars(select(User)).all())