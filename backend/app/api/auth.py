from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.database.session import get_sync_db
from app.database.models import User, Organization
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]
    organization: Dict[str, Any]

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_sync_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled")
    return user

def get_optional_user(token: Optional[str] = Depends(oauth2_optional_scheme), db: Session = Depends(get_sync_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except Exception:
        return None

ROLE_CANONICAL_MAP = {
    "ciso": "CISO",
    "ciso / approver": "CISO",
    "approver": "CISO",
    "security_analyst": "SECURITY_ANALYST",
    "security analyst": "SECURITY_ANALYST",
    "analyst": "SECURITY_ANALYST",
    "risk_analyst": "RISK_ANALYST",
    "quantitative risk analyst": "RISK_ANALYST",
    "risk analyst": "RISK_ANALYST",
    "risk": "RISK_ANALYST",
    "executive": "EXECUTIVE",
    "executive board / ceo": "EXECUTIVE",
    "ceo": "EXECUTIVE",
    "board": "EXECUTIVE",
    "auditor": "AUDITOR",
    "lead security auditor": "AUDITOR",
    "lead auditor": "AUDITOR",
    "admin": "ADMIN",
    "system administrator": "ADMIN",
    "administrator": "ADMIN"
}

def normalize_role(r: str) -> str:
    cleaned = (r or "").strip().lower()
    return ROLE_CANONICAL_MAP.get(cleaned, (r or "").upper())

def require_roles(allowed_roles: list):
    canonical_allowed = {normalize_role(r) for r in allowed_roles}
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_norm = normalize_role(current_user.role)
        if user_role_norm != "ADMIN" and user_role_norm not in canonical_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{current_user.role}'. Required: {allowed_roles}"
            )
        return current_user
    return role_checker

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_sync_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    token = create_access_token(subject=user.id, role=user.role, org_id=user.organization_id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        },
        "organization": {
            "id": org.id,
            "name": org.name,
            "industry": org.industry,
            "annual_revenue": org.annual_revenue,
            "cybersecurity_budget": org.cybersecurity_budget
        }
    }

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password does not match.")
    
    if len(request.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be at least 6 characters.")
    
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {
        "status": "SUCCESS",
        "message": "Password updated successfully."
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "organization": {
            "id": org.id,
            "name": org.name,
            "industry": org.industry,
            "annual_revenue": org.annual_revenue,
            "cybersecurity_budget": org.cybersecurity_budget,
            "risk_appetite_enterprise": org.risk_appetite_enterprise,
            "risk_appetite_critical_asset": org.risk_appetite_critical_asset
        }
    }
