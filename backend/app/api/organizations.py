from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.database.session import get_sync_db
from app.database.models import Organization
from app.api.auth import get_current_user

router = APIRouter(prefix="/organizations", tags=["Organization Management"])

class UpdateOrgRequest(BaseModel):
    name: Optional[str] = None
    annual_revenue: Optional[float] = None
    cybersecurity_budget: Optional[float] = None
    risk_appetite_enterprise: Optional[float] = None
    risk_appetite_critical_asset: Optional[float] = None
    financial_assumptions: Optional[Dict[str, Any]] = None

@router.get("/current")
def get_current_org(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/current")
def update_current_org(request: UpdateOrgRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if request.name is not None:
        org.name = request.name
    if request.annual_revenue is not None:
        org.annual_revenue = request.annual_revenue
    if request.cybersecurity_budget is not None:
        org.cybersecurity_budget = request.cybersecurity_budget
    if request.risk_appetite_enterprise is not None:
        org.risk_appetite_enterprise = request.risk_appetite_enterprise
    if request.risk_appetite_critical_asset is not None:
        org.risk_appetite_critical_asset = request.risk_appetite_critical_asset
    if request.financial_assumptions is not None:
        org.financial_assumptions = request.financial_assumptions
    
    db.commit()
    db.refresh(org)
    return org
