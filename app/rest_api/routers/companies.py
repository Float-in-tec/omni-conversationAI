from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db_utils.deps import get_db
from app.rest_api.schemas.company import CompanyCreate, CompanyOut
from app.services.company_service import create_company, list_companies, get_company

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company_endpoint(payload: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, name=payload.name)

@router.get("", response_model=list[CompanyOut])
def list_companies_endpoint(db: Session = Depends(get_db)):
    return list_companies(db)

@router.get("/{company_id}", response_model=CompanyOut)
def get_company_endpoint(company_id: int, db: Session = Depends(get_db)):
    company = get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
