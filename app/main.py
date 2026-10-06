from fastapi import FastAPI
from dotenv import load_dotenv

from app.movements.routes import router as movements_router

import os

load_dotenv()

app = FastAPI()

app.include_router(movements_router)

@app.get("/")
def root():
    return {"message": "FINGO API funcionando"}
