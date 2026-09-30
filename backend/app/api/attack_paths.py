from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_sync_db
from app.api.auth import get_current_user
from app.attack_paths.analyzer import attack_path_engine
from app.risk_engine.universal_importer import universal_csv_engine

router = APIRouter(prefix="/attack-paths", tags=["Attack Path Analysis & Graph Visualizer"])

@router.get("")
def get_attack_paths(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    active_ds = universal_csv_engine.get_active_dataset()
    data = attack_path_engine.get_attack_graph_data(active_ds=active_ds)
    return data

@router.get("/critical")
def get_critical_attack_path(current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    """Returns the primary crown jewel critical attack path with mitigation recommendations."""
    active_ds = universal_csv_engine.get_active_dataset()
    data = attack_path_engine.get_attack_graph_data(active_ds=active_ds)
    critical_paths = data.get("critical_attack_paths", [])
    if not critical_paths:
        return {
            "status": "UNAVAILABLE",
            "message": "Attack path cannot be determined from available dataset.",
            "data_source": data.get("data_source", "Active Dataset")
        }
    return critical_paths[0]

@router.get("/{path_id}")
def get_attack_path_detail(path_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_sync_db)):
    active_ds = universal_csv_engine.get_active_dataset()
    data = attack_path_engine.get_attack_graph_data(active_ds=active_ds)
    for p in data.get("critical_attack_paths", []):
        if p["id"] == path_id:
            return p
    critical_paths = data.get("critical_attack_paths", [])
    if critical_paths:
        return critical_paths[0]
    raise HTTPException(status_code=404, detail="Attack path not found")

