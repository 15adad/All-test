import uvicorn
from fastapi import FastAPI, Query, Depends

app=FastAPI()

async def common_p(
        skip: int = Query(0,ge=0),
        limit: int = Query(10,le=20),
):
    return {"skip":skip,"limit":limit}

@app.get("/page")
async def one(commons=Depends(common_p)):
    return {"commons":commons}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)