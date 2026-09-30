from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.database.session import get_sync_db
from app.database.models import SecurityControl
from app.api.auth import get_current_user
from app.assistant.decision_agent import decision_assistant

router = APIRouter(prefix="/assistant", tags=["Controlled AI Decision Assistant"])

class AssistantQueryRequest(BaseModel):
    query: str

@router.post("/query")
def ask_assistant(request: AssistantQueryRequest, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    controls = db.query(SecurityControl).filter(SecurityControl.organization_id == current_user.organization_id).all()
    context = {
        "user_name": current_user.full_name,
        "role": current_user.role,
        "controls": [
            {
                "code": c.code,
                "name": c.name,
                "implementation_cost": c.implementation_cost,
                "modeled_risk_reduction": c.modeled_risk_reduction
            }
            for c in controls
        ]
    }
    response = decision_assistant.answer_query(query=request.query, context_data=context)
    return response
