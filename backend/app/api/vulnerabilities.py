from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database.session import get_sync_db
from app.database.models import Vulnerability, Asset
from app.api.auth import get_current_user

router = APIRouter(prefix="/vulnerabilities", tags=["Vulnerability Management"])

@router.get("")
def list_vulnerabilities(
    severity: Optional[str] = Query(None),
    active_exploit_only: Optional[bool] = Query(None),
    remediation_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    query = db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id)
    
    if severity:
        query = query.filter(Vulnerability.severity == severity.upper())
    if active_exploit_only:
        query = query.filter(Vulnerability.active_exploitation == True)
    if remediation_status:
        query = query.filter(Vulnerability.remediation_status == remediation_status.upper())
    if search:
        query = query.filter(Vulnerability.cve_id.ilike(f"%{search}%") | Vulnerability.title.ilike(f"%{search}%"))
        
    vulns = query.order_by(Vulnerability.cvss_score.desc()).limit(limit).all()
    
    stats = {
        "total": db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id).count(),
        "critical": db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id, Vulnerability.severity == "CRITICAL").count(),
        "high": db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id, Vulnerability.severity == "HIGH").count(),
        "medium": db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id, Vulnerability.severity == "MEDIUM").count(),
        "low": db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id, Vulnerability.severity == "LOW").count(),
        "cisa_known_exploited": db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id, Vulnerability.active_exploitation == True).count()
    }
    
    return {
        "items": vulns,
        "stats": stats
    }

@router.get("/{vuln_id}")
def get_vulnerability(vuln_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id, Vulnerability.organization_id == current_user.organization_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    asset = db.query(Asset).filter(Asset.id == vuln.affected_asset_id).first()
    return {
        "vulnerability": vuln,
        "affected_asset": asset
    }

class VulnerabilityCreateRequest(BaseModel):
    affected_asset_id: str
    cve_id: str
    title: str
    description: Optional[str] = None
    cvss_score: float = 7.5
    severity: Optional[str] = None
    exploit_available: bool = False
    active_exploitation: bool = False
    patch_available: bool = True
    source: str = "Scanner / Manual"

@router.post("")
def create_vulnerability(request: VulnerabilityCreateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    sev = request.severity or ("CRITICAL" if request.cvss_score >= 9.0 else ("HIGH" if request.cvss_score >= 7.0 else "MEDIUM"))
    vuln = Vulnerability(
        organization_id=current_user.organization_id,
        affected_asset_id=request.affected_asset_id,
        cve_id=request.cve_id,
        title=request.title,
        description=request.description or f"Vulnerability {request.cve_id} detected.",
        cvss_score=request.cvss_score,
        severity=sev.upper(),
        exploit_available=request.exploit_available,
        active_exploitation=request.active_exploitation,
        patch_available=request.patch_available,
        remediation_status="OPEN",
        source=request.source
    )
    db.add(vuln)
    db.commit()
    db.refresh(vuln)
    return vuln

