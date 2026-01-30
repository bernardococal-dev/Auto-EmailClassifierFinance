import os
from fastapi import FastAPI
from app.api import documents
from app.db import init_db

app = FastAPI(title="Auto Email Classifier - Finance")

app.include_router(documents.router, prefix="/documentos", tags=["documentos"])

@app.on_event("startup")
def startup_event():
    # Initialize DB (create tables)
    init_db.create_tables()

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Auto Email Classifier - Finance"}
