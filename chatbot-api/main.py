from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from app.routes import router

app = FastAPI(
    title="聊天机器人 API",
    description="一个支持多轮对话和流式输出的聊天机器人",
    version="1.0.0"
)
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
