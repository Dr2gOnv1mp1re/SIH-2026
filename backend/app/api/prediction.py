"""
XGBoost Future Risk Prediction & SHAP REST API Router.
Provides exact routes specified in Master Development Prompt Section 5:
- POST /api/prediction/train
- POST /api/prediction/predict
- GET  /api/prediction/latest
- GET  /api/prediction/shap
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.database.session import get_sync_db
from app.database.models import RiskAssessment, Vulnerability, Asset
from app.api.auth import get_current_user
from app.ml.model_registry import model_registry
from app.ml.training import train_risk_models
from app.ml.feature_engineering import FEATURE_NAMES
from app.risk_engine.universal_importer import universal_csv_engine

router = APIRouter(prefix="/prediction", tags=["AI Future-Risk Prediction & SHAP (XGBoost)"])

class PredictCustomRequest(BaseModel):
    features: Optional[Dict[str, float]] = None
    current_eal: Optional[float] = None

@router.post("/train")
def train_prediction_model(current_user = Depends(get_current_user)):
    """Trains or re-trains the XGBoost regressor and baseline Random Forest."""
    res = train_risk_models(n_samples=400, seed=42)
    model_registry.xgb_model = res["xgb_model"]
    model_registry.rf_baseline_model = res["rf_model"]
    model_registry.model_metadata["metrics"] = res["metrics"]
    model_registry.model_metadata["trained_at"] = res["trained_at"]
    model_registry.model_metadata["feature_set"] = FEATURE_NAMES
    model_registry.predictor.set_model(res["xgb_model"])
    return {
        "status": "SUCCESS",
        "message": "XGBoost model and Random Forest baseline successfully trained.",
        "metrics": res["metrics"],
        "trained_at": res["trained_at"],
        "model_version": model_registry.model_metadata.get("version", "v2.5.0")
    }

@router.get("/models")
def get_model_metadata(current_user = Depends(get_current_user)):
    """Returns model versioning, feature set, and validation metrics (MAE, RMSE, R2)."""
    if model_registry.xgb_model is None:
        model_registry.train_or_initialize()
    return {
        "model_id": "model-xgb-risk-regressor",
        "model_version": model_registry.model_metadata.get("version", "v2.5.0"),
        "model_type": model_registry.model_metadata.get("model_type", "XGBoost Regressor"),
        "trained_at": model_registry.model_metadata.get("trained_at"),
        "metrics": model_registry.model_metadata.get("metrics", {}),
        "feature_set": FEATURE_NAMES,
        "evaluation_description": "Cross-validated regression against simulated enterprise compromise trajectories. Metrics reported on 20% holdout test partition."
    }

@router.post("/predict")
def predict_custom_risk(
    request: PredictCustomRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Executes future risk prediction for specified feature vector."""
    latest_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.organization_id == current_user.organization_id
    ).order_by(RiskAssessment.timestamp.desc()).first()
    eal = request.current_eal if request.current_eal else (latest_assessment.expected_annual_loss if latest_assessment else 46000000.0)

    features = request.features or {
        "vulnerability_count": 50.0,
        "mean_cvss_score": 8.4,
        "active_exploit_count": 6.0,
        "asset_criticality_avg": 88.0,
        "internet_exposed_ratio": 0.35,
        "control_effectiveness_avg": 70.0,
        "unpatched_cve_count": 50.0,
        "historical_incident_rate": 2.0,
        "threat_actor_activity_level": 90.0,
        "attack_path_depth": 5.0
    }

    return model_registry.predict(features, current_eal=eal)

@router.get("/latest")
@router.get("/future-risk")
def get_latest_prediction(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Returns 30/60/90-day predictions based on active dataset or organization telemetry."""
    latest_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.organization_id == current_user.organization_id
    ).order_by(RiskAssessment.timestamp.desc()).first()
    eal = latest_assessment.expected_annual_loss if latest_assessment else 46000000.0

    active_ds = universal_csv_engine.get_active_dataset()
    if active_ds and active_ds.get("assets"):
        raw_assets = active_ds.get("assets", [])
        raw_vulns = active_ds.get("vulnerabilities", [])
        dataset_name = active_ds.get("filename") or "Active Uploaded Dataset"
        
        vuln_count = len(raw_vulns) if raw_vulns else len(raw_assets)
        cvss_vals = [float(v.get("cvss_score") or 7.0) for v in raw_vulns] if raw_vulns else [7.5]
        mean_cvss = sum(cvss_vals) / len(cvss_vals) if cvss_vals else 7.5
        active_exploits = sum(1 for v in raw_vulns if v.get("exploit_available") or v.get("active_exploitation"))
        exposed_count = sum(1 for a in raw_assets if a.get("internet_exposed"))
        crit_vals = [float(a.get("criticality_score") or (float(a.get("asset_criticality_1_5", 3.0))*20.0)) for a in raw_assets]
        mean_crit = sum(crit_vals) / len(crit_vals) if crit_vals else 75.0
        ctrl_vals = [float(a.get("control_effectiveness") or 0.65) for a in raw_assets]
        mean_ctrl = (sum(ctrl_vals) / len(ctrl_vals)) * 100.0 if (ctrl_vals and sum(ctrl_vals)/len(ctrl_vals) <= 1.0) else 65.0

        features = {
            "asset_id": "ACTIVE_DATASET_ENTERPRISE",
            "vulnerability_count": float(vuln_count),
            "mean_cvss_score": round(mean_cvss, 1),
            "active_exploit_count": float(active_exploits),
            "asset_criticality_avg": round(mean_crit, 1),
            "internet_exposed_ratio": round(float(exposed_count) / max(1.0, float(len(raw_assets))), 2),
            "control_effectiveness_avg": round(mean_ctrl, 1),
            "unpatched_cve_count": float(vuln_count),
            "historical_incident_rate": 2.0,
            "threat_actor_activity_level": 85.0 if active_exploits > 0 else 60.0,
            "attack_path_depth": 5.0,
            "data_source": dataset_name
        }
    else:
        vuln_count = db.query(Vulnerability).filter(Vulnerability.organization_id == current_user.organization_id).count()
        active_exploits = db.query(Vulnerability).filter(
            Vulnerability.organization_id == current_user.organization_id,
            Vulnerability.active_exploitation == True
        ).count()
        internet_exposed = db.query(Asset).filter(
            Asset.organization_id == current_user.organization_id,
            Asset.internet_exposed == True
        ).count()

        features = {
            "asset_id": "ENTERPRISE_BASELINE_ABC_BANK",
            "vulnerability_count": float(vuln_count),
            "mean_cvss_score": 8.4,
            "active_exploit_count": float(active_exploits),
            "asset_criticality_avg": 88.0,
            "internet_exposed_ratio": float(internet_exposed) / max(1.0, float(vuln_count)),
            "control_effectiveness_avg": 70.0,
            "unpatched_cve_count": 50.0,
            "historical_incident_rate": 2.0,
            "threat_actor_activity_level": 90.0,
            "attack_path_depth": 5.0,
            "data_source": "Enterprise Baseline Database (ABC Bank)"
        }

    return model_registry.predict(features, current_eal=eal)

@router.get("/shap")
@router.get("/shap-explanation")
def get_shap_factors(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Returns local SHAP feature attributions and driver directions."""
    latest = get_latest_prediction(current_user=current_user, db=db)
    return {
        "model": "XGBoost TreeExplainer",
        "baseline_comparison": "Random Forest Regressor",
        "shap_factors": latest.get("shap_explanation", []),
        "top_positive_risk_drivers": latest.get("top_positive_risk_drivers", []),
        "top_negative_risk_drivers": latest.get("top_negative_risk_drivers", []),
        "why_is_model_predicting_higher_risk": latest.get("why_is_model_predicting_higher_risk", ""),
        "trend": latest.get("trend", "INCREASING"),
        "confidence_percentage": latest.get("confidence_percentage", 82.0),
        "modeled_label": "SHAP FEATURE ATTRIBUTION"
    }
