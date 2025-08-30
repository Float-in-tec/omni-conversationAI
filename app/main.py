from fastapi import FastAPI, Depends
from app.db_utils.db_connection import DBConn

app = FastAPI(title="omniAI")

@app.on_event("startup")
def startup_event():
    # Initialize DBConn on startup to validate DB availability
    db = DBConn()
    db.connect()
    db.disconnect()

@app.get("/health")
def health_check():
    return {"status": "ok"}
