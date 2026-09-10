from fastapi import FastAPI,Path,Query
app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int = Path(..., ge=1, le=50, description="一个示例")):
    return {"item_id": item_id,"test":123}

@app.get("/news/news_list")
async def news_list(skip:int=Query(description="跳过的数",lt=100),limit:int=10):
    return {"skip":skip,"limit":limit}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("demo6:app", host="127.0.0.1", port=8000, reload=True)
