from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import User
from app.schemas import RegisterResponse, RegisterRequest
from app.security import hash_password, verify_password, create_access_token, decode_token,create_refresh_token

router = APIRouter(prefix="/auth",tags=["用户认证"])

# 用户注册登录
@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_async_session)):
    stmt = select(User).where(User.username == request.username)
    result = (await db.execute(stmt)).one_or_none()
    if result:
        raise HTTPException(status_code=400, detail="用户名已存在")
    # 调用JWT认证函数，生成JWT token
    access_token = create_access_token(request.username)
    new_user = User(username=request.username, hashed_password=hash_password(request.password),id=access_token)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"token":access_token}

@router.post("/login",response_model=RegisterResponse)
async def login(token: str, request: RegisterRequest, db: AsyncSession = Depends(get_async_session) ):
    stmt = select(User).where((User.username == request.username)&(User.id==token))
    result = (await db.execute(stmt)).one_or_none()
    if not result:
        raise HTTPException(status_code=400, detail="用户名不存在")
    if not verify_password(request.password, result.hashed_password):
        raise HTTPException(status_code=400, detail="密码错误")
    # 验证token


