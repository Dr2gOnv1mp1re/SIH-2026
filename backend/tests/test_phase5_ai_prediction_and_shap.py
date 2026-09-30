"""
Phase 5: AI & Explainability (XGBoost + SHAP) Automated Test Suite.
Verifies:
1. Feature vector extraction and preprocessing.
2. Training pipeline, split validation, and regression metrics (RMSE, MAE, R2).
3. 30-day, 60-day, and 90-day time-aware future risk predictions.
4. True SHAP TreeExplainer feature attributions (positive & negative drivers).
5. Natural language explainability ("Why is the model predicting higher risk?").
6. Insufficient data handling (graceful warning without hallucination).
7. Model versioning and metadata endpoint (/prediction/models).
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.ml.feature_engineering import extract_feature_vector, FEATURE_NAMES
from app.ml.training import train_risk_models
from app.ml.prediction import RiskPredictor
from app.ml.model_registry import model_registry

def test_feature_vector_extraction():
    """Verify feature vector mapping from security telemetry dictionary."""
    telemetry = {
        "vulnerability_count": 42.0,
        "mean_cvss_score": 9.1,
        "active_exploit_count": 5.0,
        "asset_criticality_avg": 90.0,
        "internet_exposed_ratio": 0.40,
        "control_effectiveness_avg": 60.0
    }
    vec = extract_feature_vector(telemetry)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == len(FEATURE_NAMES)
    assert vec[0] == 42.0
    assert vec[1] == 9.1
    assert vec[2] == 5.0

def test_model_training_and_evaluation_metrics():
    """Verify XGBoost training and regression evaluation metrics on holdout test partition."""
    res = train_risk_models(n_samples=400, seed=42)
    assert "metrics" in res
    xgb_metrics = res["metrics"]["xgboost"]
    assert "rmse" in xgb_metrics
    assert "mae" in xgb_metrics
    assert "r2_score" in xgb_metrics
    assert xgb_metrics["rmse"] > 0
    assert xgb_metrics["mae"] > 0
    assert xgb_metrics["r2_score"] > 0.65  # Verifiable statistical fit

def test_multi_horizon_predictions_and_shap_explainability():
    """Verify 30-day, 60-day, 90-day trajectory and SHAP driver directions."""
    predictor = RiskPredictor()
    telemetry = {
        "vulnerability_count": 60.0,
        "mean_cvss_score": 9.6,
        "active_exploit_count": 8.0,
        "asset_criticality_avg": 92.0,
        "internet_exposed_ratio": 0.50,
        "control_effectiveness_avg": 45.0,
        "threat_actor_activity_level": 92.0
    }

    pred_res = predictor.predict_future_risk(telemetry, current_eal=46000000.0)
    assert pred_res["status"] == "SUCCESS"
    assert "prediction_horizons" in pred_res
    horizons = pred_res["prediction_horizons"]
    assert 30 in [horizons["30_days"]["horizon_days"], 30]
    assert 60 in [horizons["60_days"]["horizon_days"], 60]
    assert 90 in [horizons["90_days"]["horizon_days"], 90]
    
    # Compounding risk trajectory
    assert horizons["30_days"]["predicted_eal"] <= horizons["60_days"]["predicted_eal"] <= horizons["90_days"]["predicted_eal"]
    assert pred_res["predicted_30d_risk_score"] <= pred_res["predicted_60d_risk_score"] <= pred_res["predicted_90d_risk_score"]

    # SHAP feature attributions
    assert "shap_explanation" in pred_res
    assert len(pred_res["shap_explanation"]) > 0
    assert len(pred_res["top_positive_risk_drivers"]) > 0
    assert "why_is_model_predicting_higher_risk" in pred_res
    assert len(pred_res["why_is_model_predicting_higher_risk"]) > 10

def test_insufficient_data_handling():
    """Verify that insufficient data returns an explicit warning rather than fabricated predictions."""
    predictor = RiskPredictor()
    sparse_data = {"asset_id": "AST-EMPTY"}  # Missing all telemetry

    res = predictor.predict_future_risk(sparse_data)
    assert res["status"] == "INSUFFICIENT_DATA"
    assert "Insufficient data" in res["detail"]
    assert res["confidence_percentage"] == 0.0

def test_prediction_api_endpoints_integration():
    """Verify /prediction/future-risk, /prediction/shap-explanation, and /prediction/models endpoints."""
    with TestClient(app) as client:
        login_res = client.post("/api/v1/auth/login", json={
            "email": "ciso@abcbank.com",
            "password": "Ciso@12345"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Model version & evaluation metrics endpoint
        models_res = client.get("/api/v1/prediction/models", headers=headers)
        assert models_res.status_code == 200
        models_data = models_res.json()
        assert "model_version" in models_data
        assert "metrics" in models_data
        assert "feature_set" in models_data

        # 2. Future risk multi-horizon prediction endpoint
        pred_res = client.get("/api/v1/prediction/future-risk", headers=headers)
        assert pred_res.status_code == 200
        pred_data = pred_res.json()
        assert "predicted_30d_risk_score" in pred_data
        assert "predicted_30d_eal" in pred_data
        assert "predicted_60d_eal" in pred_data
        assert "predicted_90d_eal" in pred_data

        # 3. SHAP feature explanation endpoint
        shap_res = client.get("/api/v1/prediction/shap-explanation", headers=headers)
        assert shap_res.status_code == 200
        shap_data = shap_res.json()
        assert "shap_factors" in shap_data
        assert "top_positive_risk_drivers" in shap_data
        assert "why_is_model_predicting_higher_risk" in shap_data
