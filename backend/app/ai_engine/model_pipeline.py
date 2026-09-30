"""
Backwards-compatible bridge forwarding to modular ML engine in app.ml.
Maintains ml_engine singleton with train_or_initialize_models() and predict_future_risk().
"""

from typing import Dict, Any, Optional
from app.ml.model_registry import model_registry
from app.ml.feature_engineering import FEATURE_NAMES

class CyberRiskMLEngine:
    def __init__(self):
        self.feature_names = FEATURE_NAMES
        self.model_metadata = model_registry.model_metadata

    @property
    def xgb_model(self):
        return model_registry.xgb_model

    @property
    def explainer(self):
        return model_registry.predictor.explainer.explainer

    def train_or_initialize_models(self):
        model_registry.train_or_initialize()

    def predict_future_risk(
        self,
        features: Dict[str, float],
        current_eal: float = 46000000.0,
        sufficient_history: bool = True
    ) -> Dict[str, Any]:
        return model_registry.predict(features, current_eal=current_eal)

ml_engine = CyberRiskMLEngine()

__all__ = ["ml_engine", "CyberRiskMLEngine"]
