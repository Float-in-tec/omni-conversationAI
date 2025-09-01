# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db_utils.deps import get_db
from app.dao.users import DAOUser

router = APIRouter()

@router.get("/companies/{company_id}/users")
def list_company_users(company_id: int, db: Session = Depends(get_db)):
    users = db.query(DAOUser).filter(DAOUser.company_id == company_id).order_by(DAOUser.id.asc()).all()
    return [{"id": u.id, "name": u.name, "role": u.role} for u in users]
