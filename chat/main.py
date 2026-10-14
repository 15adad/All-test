from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers.auth import router as user_router

app = FastAPI()
app.include_router(user_router)

# 中间件处理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
