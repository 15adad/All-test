from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """把明文密码哈希，存数据库用这个"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证用户输入的密码是否匹配数据库里的哈希值"""
    return pwd_context.verify(plain_password, hashed_password)

# JWT 认证
def create_access_token(user_id: int, username: str) -> str:
    """生成 Access Token"""
    now = datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(user_id),              # 主题：用户ID（JWT 要求 sub 是字符串）
        "username": username,
        "type": "access",                  # 区分 token 类型
        "iat": now,                        # 签发时间
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """生成 Refresh Token"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ============================================================
# JWT 验证
# ============================================================
def decode_token(token: str) -> dict[str, Any]:
    """解析 JWT，失败抛异常"""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token 已过期")
    except jwt.InvalidTokenError:
        raise ValueError("Token 无效")