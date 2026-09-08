from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def root():
    return {"message": "hello world"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
