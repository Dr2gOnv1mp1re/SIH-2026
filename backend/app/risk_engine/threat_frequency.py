"""
Threat Event Frequency (TEF) calculations based on FAIR quantitative risk principles.
Evaluates the frequency (events per year) with which a threat agent is expected to act against an asset.
"""

from typing import Dict, Any

def calculate_threat_event_frequency(
    threat_activity_level: float,     # 0-100 (from threat intel / active campaigns)
    is_internet_facing: bool = False,
    is_targeted_sector: bool = True,  # e.g. Banking sector targeted by FIN7 / LockBit
    has_active_cve_exploit: bool = False
) -> Dict[str, Any]:
    """
    Computes Threat Event Frequency (TEF) in events / year.
    Formula:
        TEF = Base Contact Frequency * Sector Targeting Multiplier * Exploit Weaponization Multiplier
    """
    # Baseline contact rate per year (0.1 to 3.0 events/year for enterprise systems)
    base_tef = (threat_activity_level / 100.0) * 1.5

    # Multipliers
    sector_mult = 1.30 if is_targeted_sector else 1.0
    exposure_mult = 1.40 if is_internet_facing else 1.0
    exploit_mult = 1.50 if has_active_cve_exploit else 1.0

    tef_value = round(base_tef * sector_mult * exposure_mult * exploit_mult, 2)
    # Clamp to reasonable enterprise bounds [0.05, 12.0] events/year
    tef_value = max(0.05, min(12.0, tef_value))

    return {
        "threat_event_frequency": tef_value,
        "threat_activity_level": threat_activity_level,
        "is_internet_facing": is_internet_facing,
        "is_targeted_sector": is_targeted_sector,
        "has_active_cve_exploit": has_active_cve_exploit,
        "frequency_unit": "events / year",
        "modeled_label": "MODELED FREQUENCY"
    }
