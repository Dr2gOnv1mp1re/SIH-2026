"""
Data Sources & Data Provenance API Router.
Exposes categorized lineage for judges, auditors, and CISOs:
1. REAL PUBLIC DATA
2. SECURITY TELEMETRY
3. ORGANIZATION DATA
4. SYNTHETIC DEMO DATA
5. MODEL OUTPUT
"""

from fastapi import APIRouter, Depends
from app.api.auth import get_current_user
from app.provenance.data_provenance import get_all_provenance_sources, get_provenance_by_category

router = APIRouter(prefix="/provenance", tags=["Data Sources & Provenance Registry"])

@router.get("")
def get_provenance(current_user = Depends(get_current_user)):
    """Returns the full categorized data provenance registry."""
    return get_all_provenance_sources()

@router.get("/category/{category_name}")
def get_category_provenance(category_name: str, current_user = Depends(get_current_user)):
    """Returns data provenance sources for a specific category."""
    return get_provenance_by_category(category_name)
