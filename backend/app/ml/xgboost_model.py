"""
XGBoost Cyber Risk Regressor Model Definition.
Wraps XGBoost Regressor with hyperparameters tuned for enterprise tabular telemetry.
"""

from typing import Dict, Any, Optional

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    from sklearn.ensemble import RandomForestRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def build_xgboost_regressor(params: Optional[Dict[str, Any]] = None):
    """Initializes an XGBoost Regressor."""
    if not HAS_XGBOOST:
        return None
    default_params = {
        "n_estimators": 35,
        "max_depth": 3,
        "learning_rate": 0.08,
        "subsample": 0.85,
        "random_state": 42,
        "n_jobs": 1
    }
    if params:
        default_params.update(params)
    return xgb.XGBRegressor(**default_params)

def build_rf_baseline(params: Optional[Dict[str, Any]] = None):
    """Initializes a Random Forest baseline regressor."""
    if not HAS_SKLEARN:
        return None
    default_params = {
        "n_estimators": 30,
        "max_depth": 4,
        "random_state": 42,
        "n_jobs": 1
    }
    if params:
        default_params.update(params)
    return RandomForestRegressor(**default_params)
