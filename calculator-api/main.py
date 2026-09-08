from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="计算器 API",
    description="一个简单的四则运算计算器",
    version="1.0.0"
)

# 注册路由
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)