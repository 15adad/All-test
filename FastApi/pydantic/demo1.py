import re
from typing import List

from pydantic import BaseModel, Field, field_validator
from sklearn.externals.array_api_compat.torch import equal


class UserSignup(BaseModel):
    username: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=8, max_length=32)
    age: int = Field(..., ge=18, le=120)
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$')
    nickname: str = Field(default="")
    tags: List[str] = Field(default_factory=list)  # 注意：默认值是可变对象要用 default_factory

    # 自定义校验器
    @field_validator("password")
    def valid_password(cls, v: str) -> str:
        # 正则表达式 ->str表示返回一个字符串
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        return v


class Address(BaseModel):
    # TODO 9: 省（必填）
    province: str = Field(..., min_length=1)
    # TODO 10: 市（必填）
    city: str = Field(..., min_length=1)
    # TODO 11: 详细地址（必填）
    detail: str = Field(..., min_length=1)


class UserProfile(BaseModel):
    user: UserSignup
    address: List[Address] = Field(..., min_length=1)
    agree_term: bool = Field(..., equal=True)

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 开始测试 Pydantic 练习")
    print("=" * 50)

    # ---------- 测试 1：正确数据（应该通过） ----------
    print("\n✅ 测试 1: 正确数据（预期：通过）")
    try:
        valid_data = {
            "username": "alice_123",
            "password": "Password123",
            "age": 25,
            "email": "alice@example.com",
            "nickname": "Alice",
            "tags": ["python", "fastapi"]
        }
        user1 = UserSignup(**valid_data)
        print(f"✅ 通过！用户名: {user1.username}, 邮箱: {user1.email}")
        print(f"   tags: {user1.tags}")
    except Exception as e:
        print(f"❌ 失败: {e}")

    # ---------- 测试 2：缺少必填字段（预期：报错） ----------
    print("\n❌ 测试 2: 缺少 username（预期：报错）")
    try:
        invalid_data = {
            "password": "Password123",
            "age": 25,
            "email": "alice@example.com"
        }
        user2 = UserSignup(**invalid_data)
        print("❌ 不应该通过！")
    except Exception as e:
        print(f"✅ 正确报错: {type(e).__name__}")

    # ---------- 测试 3：密码太弱（预期：报错） ----------
    print("\n❌ 测试 3: 密码没有大写字母（预期：报错）")
    try:
        invalid_data = {
            "username": "bob",
            "password": "password123",  # 没有大写
            "age": 30,
            "email": "bob@example.com"
        }
        user3 = UserSignup(**invalid_data)
        print("❌ 不应该通过！")
    except Exception as e:
        print(f"✅ 正确报错: {e}")

    # ---------- 测试 4：年龄超标（预期：报错） ----------
    print("\n❌ 测试 4: 年龄 150 岁（预期：报错）")
    try:
        invalid_data = {
            "username": "charlie",
            "password": "Charlie123",
            "age": 150,
            "email": "charlie@example.com"
        }
        user4 = UserSignup(**invalid_data)
        print("❌ 不应该通过！")
    except Exception as e:
        print(f"✅ 正确报错: {e}")

    # ---------- 测试 5：嵌套模型（正确数据） ----------
    print("\n✅ 测试 5: 完整的嵌套模型（预期：通过）")
    try:
        full_data = {
            "user": {
                "username": "david_99",
                "password": "SecurePass1",
                "age": 28,
                "email": "david@work.com"
            },
            "addresses": [
                {"province": "广东省", "city": "深圳市", "detail": "南山区科技园"}
            ],
            "agree_terms": True
        }
        profile = UserProfile(**full_data)
        print(f"✅ 通过！用户名: {profile.user.username}")
        print(f"   地址数量: {len(profile.addresses)}")
        print(f"   是否同意协议: {profile.agree_terms}")
    except Exception as e:
        print(f"❌ 失败: {e}")

    # ---------- 测试 6：未同意协议（预期：报错） ----------
    print("\n❌ 测试 6: agree_terms = False（预期：报错）")
    try:
        invalid_terms = {
            "user": {
                "username": "eve",
                "password": "EveSecure1",
                "age": 22,
                "email": "eve@test.com"
            },
            "addresses": [
                {"province": "北京", "city": "北京市", "detail": "海淀区"}
            ],
            "agree_terms": False
        }
        profile2 = UserProfile(**invalid_terms)
        print("❌ 不应该通过！")
    except Exception as e:
        print(f"✅ 正确报错: {e}")

    print("\n" + "=" * 50)
    print("🎉 练习结束！检查你的 TODO 是否全部完成。")
    print("=" * 50)