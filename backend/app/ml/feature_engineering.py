"""
Feature Engineering Pipeline for XGBoost Cyber Risk Regressor.
Extracts normalized numerical feature vectors from enterprise telemetry,
ensuring consistent feature ordering for training and inference.
"""

from typing import Dict, List, Any
import numpy as np

FEATURE_NAMES = [
    "vulnerability_count",
    "mean_cvss_score",
    "active_exploit_count",
    "asset_criticality_avg",
    "internet_exposed_ratio",
    "control_effectiveness_avg",
    "unpatched_cve_count",
    "historical_incident_rate",
    "threat_actor_activity_level",
    "attack_path_depth",
    "control_coverage_pct",
    "vulnerability_age_avg_days"
]

def extract_feature_vector(telemetry_data: Dict[str, Any]) -> np.ndarray:
    """
    Transforms raw security telemetry dictionary into a 1D numpy feature vector.
    """
    vector = [
        float(telemetry_data.get("vulnerability_count", 50.0)),
        float(telemetry_data.get("mean_cvss_score", 8.2)),
        float(telemetry_data.get("active_exploit_count", 6.0)),
        float(telemetry_data.get("asset_criticality_avg", 88.0)),
        float(telemetry_data.get("internet_exposed_ratio", 0.35)),
        float(telemetry_data.get("control_effectiveness_avg", 65.0)),
        float(telemetry_data.get("unpatched_cve_count", 24.0)),
        float(telemetry_data.get("historical_incident_rate", 2.0)),
        float(telemetry_data.get("threat_actor_activity_level", 85.0)),
        float(telemetry_data.get("attack_path_depth", 4.0)),
        float(telemetry_data.get("control_coverage_pct", 70.0)),
        float(telemetry_data.get("vulnerability_age_avg_days", 45.0))
    ]
    return np.array(vector, dtype=np.float32)

def generate_synthetic_training_data(n_samples: int = 500, seed: int = 42) -> tuple:
    """
    Generates realistic historical enterprise training data reflecting real-world cyber relationships:
    Higher CVSS, KEV weaponization, and exposure increase risk; controls decrease risk.
    """
    rng = np.random.default_rng(seed)
    X = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=np.float32)

    X[:, 0] = rng.uniform(10, 200, n_samples)       # vulnerability_count
    X[:, 1] = rng.uniform(4.0, 9.8, n_samples)      # mean_cvss_score
    X[:, 2] = rng.poisson(3, n_samples)            # active_exploit_count
    X[:, 3] = rng.uniform(30, 98, n_samples)       # asset_criticality_avg
    X[:, 4] = rng.uniform(0.05, 0.70, n_samples)   # internet_exposed_ratio
    X[:, 5] = rng.uniform(30, 95, n_samples)       # control_effectiveness_avg
    X[:, 6] = rng.uniform(5, 50, n_samples)        # unpatched_cve_count
    X[:, 7] = rng.poisson(1, n_samples)            # historical_incident_rate
    X[:, 8] = rng.uniform(10, 90, n_samples)       # threat_actor_activity_level
    X[:, 9] = rng.integers(1, 8, n_samples)        # attack_path_depth
    X[:, 10] = rng.uniform(40, 95, n_samples)      # control_coverage_pct
    X[:, 11] = rng.uniform(10, 120, n_samples)     # vulnerability_age_avg_days

    # Ground truth deterministic risk formula + realistic noise
    y = (
        X[:, 1] * 3.2 +
        X[:, 2] * 4.0 +
        X[:, 3] * 0.30 +
        X[:, 4] * 20.0 -
        X[:, 5] * 0.35 +
        X[:, 8] * 0.18 +
        X[:, 9] * 2.2 -
        X[:, 10] * 0.15 +
        X[:, 11] * 0.05 +
        rng.normal(0, 1.2, n_samples)
    )
    y = np.clip(y, 10.0, 98.0).astype(np.float32)
    return X, y
