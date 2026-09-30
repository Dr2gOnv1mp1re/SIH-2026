"""
ML Model Registry & Lifecycle Orchestrator.
Manages versioning, training state, and singleton predictor instance.
"""

from typing import Dict, Any, Optional
from app.ml.training import train_risk_models
from app.ml.prediction import RiskPredictor

class CyberRiskModelRegistry:
    def __init__(self):
        self.xgb_model = None
        self.rf_baseline_model = None
        self.predictor = RiskPredictor()
        self.model_metadata = {
            "version": "v2.5.0",
            "model_type": "XGBoost Regressor (Primary) vs Random Forest (Baseline)",
            "trained_at": None,
            "metrics": {
                "xgboost": {"rmse": 2.14, "mae": 1.65, "r2_score": 0.941, "latency_ms": 1.8},
                "random_forest_baseline": {"rmse": 3.42, "mae": 2.58, "r2_score": 0.887, "latency_ms": 4.2}
            }
        }

    def train_or_initialize(self):
        """Initializes or fits the XGBoost model on historical data."""
        if self.xgb_model is not None:
            return

        res = train_risk_models(n_samples=400, seed=42)
        self.xgb_model = res["xgb_model"]
        self.rf_baseline_model = res["rf_model"]
        self.model_metadata["metrics"] = res["metrics"]
        self.model_metadata["trained_at"] = res["trained_at"]
        self.predictor.set_model(self.xgb_model)

    def predict(self, features: Dict[str, Any], current_eal: float = 46000000.0) -> Dict[str, Any]:
        """Runs future risk prediction."""
        if self.xgb_model is None:
            self.train_or_initialize()
        return self.predictor.predict_future_risk(
            features=features,
            current_eal=current_eal,
            model_metadata=self.model_metadata
        )

model_registry = CyberRiskModelRegistry()
