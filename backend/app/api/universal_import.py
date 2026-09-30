"""
FastAPI Router for Universal Cybersecurity CSV Import.
Enables seamless upload of ANY compatible cybersecurity CSV, automatic alias mapping,
format detection, bidirectional asset <-> vulnerability relations, and dynamic risk recalculation.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import get_sync_db
from app.database.models import Dataset, AuditLog
from app.risk_engine.universal_importer import universal_csv_engine, parse_file_bytes

router = APIRouter(prefix="/universal-import", tags=["Universal Cybersecurity CSV Import"])

class MappingAnalyzeRequest(BaseModel):
    csv_content: str
    filename: Optional[str] = "dataset.csv"

class ImportExecuteRequest(BaseModel):
    csv_content: str
    filename: str = "dataset.csv"
    custom_mappings: Optional[Dict[str, str]] = None
    duplicate_strategy: str = "update_existing"

@router.post("/detect-mappings")
async def detect_mappings(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Detects column mappings and format category from uploaded CSV file.
    """
    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = content_bytes.decode("latin-1")

    analysis = universal_csv_engine.analyze_csv(content, filename=file.filename or "dataset.csv")
    if "error" in analysis:
        raise HTTPException(status_code=400, detail=analysis["error"])

    return analysis

@router.post("/analyze-raw")
def analyze_raw_csv(request: MappingAnalyzeRequest) -> Dict[str, Any]:
    """
    Analyzes raw CSV text for column detection, validation, and preview.
    """
    analysis = universal_csv_engine.analyze_csv(request.csv_content, filename=request.filename or "dataset.csv")
    if "error" in analysis:
        raise HTTPException(status_code=400, detail=analysis["error"])
    return analysis

def sync_dataset_to_db(result: Dict[str, Any], db: Session) -> None:
    """Synchronizes imported dataset metadata and audit log into SQLite/PostgreSQL."""
    try:
        ds_id = result.get("id") or result.get("dataset_id") or "dataset_custom"
        filename = result.get("filename", "dataset.csv")
        overview = result.get("overview", {})

        # Deactivate any previous active datasets
        db.query(Dataset).update({"is_active": False})

        existing = db.query(Dataset).filter(Dataset.id == ds_id).first()
        if existing:
            existing.name = filename
            existing.filename = filename
            existing.is_active = True
            existing.total_records = overview.get("total_records", 0)
            existing.valid_records = overview.get("valid_records", 0)
            existing.rejected_records = overview.get("rejected_records", 0)
            existing.mapped_fields = overview.get("mapped_fields_count", len(overview.get("mapped_fields", [])))
            existing.missing_fields = overview.get("missing_fields_count", len(overview.get("missing_fields", [])))
            existing.warnings = overview.get("warnings", [])
            existing.rejected_reasons = overview.get("rejected_reasons", [])
            existing.summary = overview
            existing.uploaded_at = datetime.utcnow()
        else:
            file_type = "ZIP" if filename.lower().endswith(".zip") else ("XLSX" if filename.lower().endswith(".xlsx") else "CSV")
            ds = Dataset(
                id=ds_id,
                name=filename,
                filename=filename,
                file_type=file_type,
                source=filename,
                is_active=True,
                total_records=overview.get("total_records", 0),
                valid_records=overview.get("valid_records", 0),
                rejected_records=overview.get("rejected_records", 0),
                mapped_fields=overview.get("mapped_fields_count", len(overview.get("mapped_fields", []))),
                missing_fields=overview.get("missing_fields_count", len(overview.get("missing_fields", []))),
                warnings=overview.get("warnings", []),
                rejected_reasons=overview.get("rejected_reasons", []),
                summary=overview,
                uploaded_at=datetime.utcnow()
            )
            db.add(ds)

        audit = AuditLog(
            organization_id="default-org",
            dataset_id=ds_id,
            action="DATASET_UPLOADED",
            resource_type="DATASET",
            resource_id=ds_id,
            details={
                "filename": filename,
                "total_records": overview.get("total_records", 0),
                "valid_records": overview.get("valid_records", 0),
                "rejected_records": overview.get("rejected_records", 0),
                "mapped_fields": overview.get("mapped_fields_count", len(overview.get("mapped_fields", [])))
            },
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        db.rollback()

@router.post("/execute")
async def execute_csv_import(
    file: Optional[UploadFile] = File(None),
    csv_content: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    custom_mappings_json: Optional[str] = Form(None),
    duplicate_strategy: str = Form("update_existing"),
    db: Session = Depends(get_sync_db)
) -> Dict[str, Any]:
    """
    Executes import, parses assets & vulnerabilities, establishes bidirectional relationships,
    and sets as the active dataset. Supports CSV and XLSX.
    """
    text_content = ""
    target_filename = filename or "dataset.csv"

    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json", ".zip"}

    if file:
        raw_name = file.filename or target_filename
        # Path traversal and null byte sanitization (Section 4 & 5)
        clean_name = os.path.basename(raw_name).replace("..", "").replace("\x00", "").strip()
        ext = os.path.splitext(clean_name.lower())[1]
        if ext and ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        target_filename = clean_name or "dataset.csv"
        content_bytes = await file.read()
        if len(content_bytes) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 25MB.")
        try:
            text_content = parse_file_bytes(content_bytes, target_filename)
        except Exception as err:
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(err)}")
    elif csv_content:
        ext = os.path.splitext(target_filename.lower())[1]
        if ext and ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        text_content = csv_content
    else:
        raise HTTPException(status_code=400, detail="No CSV/XLSX file or content provided.")

    custom_mappings = None
    if custom_mappings_json:
        try:
            custom_mappings = json.loads(custom_mappings_json)
        except Exception:
            pass

    try:
        if file and target_filename.lower().endswith(".xlsx"):
            sheets = parse_xlsx_sheets(content_bytes)
            if len(sheets) > 1:
                result = universal_csv_engine.execute_multi_file_import(
                    file_contents=sheets,
                    package_name=target_filename,
                    duplicate_strategy=duplicate_strategy
                )
            else:
                result = universal_csv_engine.execute_import(
                    csv_content=text_content,
                    filename=target_filename,
                    custom_mappings=custom_mappings,
                    duplicate_strategy=duplicate_strategy
                )
        else:
            result = universal_csv_engine.execute_import(
                csv_content=text_content,
                filename=target_filename,
                custom_mappings=custom_mappings,
                duplicate_strategy=duplicate_strategy
            )
        sync_dataset_to_db(result, db)
        return {
            "status": "SUCCESS",
            "message": f"Successfully imported and analyzed '{target_filename}'.",
            "dataset": result
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Import execution failed: {str(err)}")

@router.post("/execute-json")
def execute_csv_import_json(request: ImportExecuteRequest) -> Dict[str, Any]:
    """
    Executes import via JSON payload.
    """
    try:
        result = universal_csv_engine.execute_import(
            csv_content=request.csv_content,
            filename=request.filename,
            custom_mappings=request.custom_mappings,
            duplicate_strategy=request.duplicate_strategy
        )
        return {
            "status": "SUCCESS",
            "message": f"Successfully imported and analyzed '{request.filename}'.",
            "dataset": result
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Import execution failed: {str(err)}")

@router.get("/active")
def get_active_dataset() -> Dict[str, Any]:
    """
    Returns the currently active uploaded dataset and overview metrics.
    """
    active = universal_csv_engine.get_active_dataset()
    if not active:
        return {
            "active": False,
            "message": "No custom dataset currently uploaded."
        }
    return {
        "active": True,
        "dataset": active
    }

@router.get("/overview")
def get_imported_overview() -> Dict[str, Any]:
    """
    Returns the 13 dynamically calculated KPIs for the active imported dataset.
    """
    active = universal_csv_engine.get_active_dataset()
    if not active or not active.get("overview"):
        return {
            "status": "NO_CUSTOM_DATASET",
            "message": "No custom dataset currently active."
        }
    return active["overview"]

@router.get("/assets")
def get_imported_assets() -> List[Dict[str, Any]]:
    """
    Returns the assets from the active imported dataset, complete with associated vulnerabilities.
    """
    active = universal_csv_engine.get_active_dataset()
    if not active or not active.get("assets"):
        return []
    return active["assets"]

@router.get("/vulnerabilities")
def get_imported_vulnerabilities() -> List[Dict[str, Any]]:
    """
    Returns the vulnerabilities from the active imported dataset, complete with affected assets.
    """
    active = universal_csv_engine.get_active_dataset()
    if not active or not active.get("vulnerabilities"):
        return []
    return active["vulnerabilities"]

@router.post("/detect-package")
async def detect_package(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Detects and inspects package contents (ZIP archive or single CSV).
    Returns file-by-file categorization, record counts, and module mappings.
    """
    filename = file.filename or "package.zip"
    content_bytes = await file.read()

    if filename.lower().endswith(".zip"):
        try:
            return universal_csv_engine.analyze_zip_package(content_bytes, zip_filename=filename)
        except Exception as err:
            raise HTTPException(status_code=400, detail=f"Failed to inspect ZIP package: {str(err)}")
    else:
        try:
            content_str = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            content_str = content_bytes.decode("latin-1")
        return universal_csv_engine.analyze_csv(content_str, filename=filename)

@router.post("/execute-package")
async def execute_package_import(
    file: UploadFile = File(...),
    duplicate_strategy: str = Form("update_existing"),
    dataset_id: Optional[str] = Form(None),
    db: Session = Depends(get_sync_db)
) -> Dict[str, Any]:
    """
    Executes complete import of a ZIP package, CSV, or XLSX.
    Parses all included files, maps to modules, links asset-vulnerability relationships,
    and recalculates risk.
    """
    filename = os.path.basename(file.filename or "data_package.zip").replace("..", "").strip()
    content_bytes = await file.read()
    if len(content_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 50MB.")

    valid_exts = ('.zip', '.csv', '.xlsx', '.txt')
    if not filename.lower().endswith(valid_exts):
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{filename}'. Supported formats: CSV, XLSX, ZIP.")

    try:
        if filename.lower().endswith(".zip"):
            result = universal_csv_engine.execute_zip_import(
                zip_bytes=content_bytes,
                zip_filename=filename,
                duplicate_strategy=duplicate_strategy,
                dataset_id=dataset_id
            )
        else:
            content_str = parse_file_bytes(content_bytes, filename)
            result = universal_csv_engine.execute_import(
                csv_content=content_str,
                filename=filename,
                duplicate_strategy=duplicate_strategy,
                dataset_id=dataset_id
            )
        sync_dataset_to_db(result, db)
        return {
            "status": "SUCCESS",
            "message": f"Successfully imported data package '{filename}'.",
            "dataset": result
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Package import failed: {str(err)}")

@router.get("/datasets")
def list_stored_datasets() -> List[Dict[str, Any]]:
    """
    Returns a list of all stored/uploaded datasets in memory.
    """
    datasets = []
    for fn, ds in universal_csv_engine.stored_datasets.items():
        if isinstance(ds, dict) and ds.get("id"):
            # Avoid duplicate listings of id and filename alias
            if fn == ds.get("id") or fn == ds.get("filename"):
                if not any(d["id"] == ds.get("id") for d in datasets):
                    datasets.append({
                        "id": ds.get("id"),
                        "filename": ds.get("filename", fn),
                        "dataset_name": ds.get("overview", {}).get("dataset_name", fn),
                        "imported_at": ds.get("imported_at"),
                        "total_assets": len(ds.get("assets", [])),
                        "total_vulnerabilities": len(ds.get("vulnerabilities", [])),
                        "is_active": (universal_csv_engine.active_dataset and universal_csv_engine.active_dataset.get("id") == ds.get("id"))
                    })
    return datasets

@router.get("/datasets/{dataset_id}")
def get_dataset_by_id(dataset_id: str) -> Dict[str, Any]:
    """
    Returns details for a specific dataset ID or filename.
    """
    ds = universal_csv_engine.get_dataset(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return ds

@router.get("/assets/{asset_id}")
def get_imported_asset_by_id(asset_id: str) -> Dict[str, Any]:
    """
    Returns a specific asset and all its associated vulnerabilities from the active dataset.
    """
    active = universal_csv_engine.get_active_dataset()
    if not active or not active.get("assets"):
        raise HTTPException(status_code=404, detail="No active custom dataset.")
    
    target = next((a for a in active["assets"] if a.get("asset_id") == asset_id or a.get("asset_name") == asset_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found in active dataset.")
    return target

@router.get("/vulnerabilities/{cve_id}")
def get_imported_vulnerability_by_id(cve_id: str) -> Dict[str, Any]:
    """
    Returns a specific vulnerability and all its affected assets from the active dataset.
    """
    active = universal_csv_engine.get_active_dataset()
    if not active or not active.get("vulnerabilities"):
        raise HTTPException(status_code=404, detail="No active custom dataset.")
    
    target = next((v for v in active["vulnerabilities"] if v.get("cve_id") == cve_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Vulnerability '{cve_id}' not found in active dataset.")
    return target

@router.post("/select-dataset")
def select_stored_dataset(
    filename: str = Query(..., description="Filename or ID of stored dataset"),
    db: Session = Depends(get_sync_db)
) -> Dict[str, Any]:
    """
    Switches active custom dataset to a previously uploaded dataset.
    """
    ds = universal_csv_engine.get_dataset(filename)
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{filename}' not found.")
    universal_csv_engine.active_dataset = ds
    try:
        db.query(Dataset).update({"is_active": False})
        t_db = db.query(Dataset).filter((Dataset.id == filename) | (Dataset.filename == filename)).first()
        if t_db:
            t_db.is_active = True
        audit = AuditLog(
            organization_id="default-org",
            dataset_id=ds.get("id", filename),
            action="DATASET_ACTIVATED",
            resource_type="DATASET",
            resource_id=ds.get("id", filename),
            details={"filename": filename},
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    except Exception:
        pass

    return {
        "status": "SUCCESS",
        "message": f"Switched active dataset to '{filename}'",
        "dataset": ds
    }

# ----------------- Datasets Master Router (/api/datasets) -----------------
datasets_router = APIRouter(prefix="/datasets", tags=["Datasets"])

@datasets_router.get("")
def alias_list_datasets(db: Session = Depends(get_sync_db)) -> List[Dict[str, Any]]:
    datasets = list_stored_datasets()
    try:
        db_datasets = db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()
        for d in db_datasets:
            if not any(item["id"] == d.id for item in datasets):
                datasets.append({
                    "id": d.id,
                    "filename": d.filename,
                    "dataset_name": d.name,
                    "imported_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                    "total_assets": d.summary.get("total_assets", 0) if d.summary else 0,
                    "total_vulnerabilities": d.summary.get("total_vulnerabilities", 0) if d.summary else 0,
                    "is_active": d.is_active,
                    "total_records": d.total_records,
                    "valid_records": d.valid_records,
                    "rejected_records": d.rejected_records
                })
    except Exception:
        pass
    return datasets

@datasets_router.get("/{dataset_id}")
def alias_get_dataset(dataset_id: str, db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    ds = universal_csv_engine.get_dataset(dataset_id)
    if ds:
        return ds
    try:
        db_ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if db_ds:
            return {
                "id": db_ds.id,
                "dataset_id": db_ds.id,
                "filename": db_ds.filename,
                "imported_at": db_ds.uploaded_at.isoformat() if db_ds.uploaded_at else None,
                "overview": db_ds.summary or {
                    "total_records": db_ds.total_records,
                    "valid_records": db_ds.valid_records,
                    "rejected_records": db_ds.rejected_records,
                    "rejected_reasons": db_ds.rejected_reasons,
                    "mapped_fields": db_ds.mapped_fields,
                    "missing_fields": db_ds.missing_fields,
                    "warnings": db_ds.warnings
                },
                "assets": [],
                "vulnerabilities": []
            }
    except Exception:
        pass
    raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")

@datasets_router.post("/upload")
@datasets_router.post("/import")
async def alias_upload_dataset(
    file: UploadFile = File(...),
    duplicate_strategy: str = Form("update_existing"),
    dataset_id: Optional[str] = Form(None),
    db: Session = Depends(get_sync_db)
) -> Dict[str, Any]:
    return await execute_package_import(file=file, duplicate_strategy=duplicate_strategy, dataset_id=dataset_id, db=db)

@datasets_router.post("/{dataset_id}/activate")
def activate_dataset_by_id(dataset_id: str, db: Session = Depends(get_sync_db)) -> Dict[str, Any]:
    ds = universal_csv_engine.get_dataset(dataset_id)
    if not ds:
        db_ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not db_ds:
            raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
        db.query(Dataset).update({"is_active": False})
        db_ds.is_active = True
        db.commit()
        return {
            "status": "SUCCESS",
            "message": f"Activated dataset '{db_ds.filename}' ({db_ds.id})",
            "dataset_id": db_ds.id,
            "filename": db_ds.filename
        }
    
    universal_csv_engine.active_dataset = ds
    try:
        db.query(Dataset).update({"is_active": False})
        target_db = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if target_db:
            target_db.is_active = True
        audit = AuditLog(
            organization_id="default-org",
            dataset_id=dataset_id,
            action="DATASET_ACTIVATED",
            resource_type="DATASET",
            resource_id=dataset_id,
            details={"filename": ds.get("filename")},
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    except Exception:
        pass

    return {
        "status": "SUCCESS",
        "message": f"Activated dataset '{ds.get('filename')}' ({dataset_id})",
        "dataset_id": dataset_id,
        "dataset": ds
    }


