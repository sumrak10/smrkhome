import uvicorn

from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI()


@app.get("/")
async def hello_world():
    return JSONResponse({"message": "Hello from Windows!"})

uvicorn.run(app, host='0.0.0.0', port=8008)