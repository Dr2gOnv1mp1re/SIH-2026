"""
OpenXML Excel (.xlsx) Parser using Python Standard Library.
Zero third-party dependencies — parses .xlsx spreadsheets using zipfile and xml.etree.ElementTree.
Supports single-sheet and multi-sheet workbooks.
"""

import zipfile
import xml.etree.ElementTree as ET
import csv
import io
import posixpath
from typing import List, Dict, Optional, Tuple

def _parse_shared_strings(zf: zipfile.ZipFile) -> List[str]:
    """Extracts shared strings from sharedStrings.xml if present."""
    shared_strings: List[str] = []
    ss_files = [n for n in zf.namelist() if n.lower().endswith("sharedstrings.xml")]
    if ss_files:
        try:
            ss_xml = zf.read(ss_files[0])
            tree = ET.fromstring(ss_xml)
            for elem in tree.iter():
                if elem.tag.endswith('si'):
                    parts = [t.text or "" for t in elem.iter() if t.tag.endswith('t')]
                    shared_strings.append("".join(parts))
        except Exception:
            pass
    return shared_strings

def _parse_sheet_xml(ws_xml: bytes, shared_strings: List[str]) -> str:
    """Parses raw worksheet XML bytes into a standard CSV string."""
    ws_tree = ET.fromstring(ws_xml)
    rows: List[List[str]] = []
    for row_elem in ws_tree.iter():
        if row_elem.tag.endswith('row'):
            cell_values = []
            for cell in row_elem:
                if cell.tag.endswith('c'):
                    cell_type = cell.attrib.get('t', '')
                    val_tag = None
                    for child in cell:
                        if child.tag.endswith('v') or child.tag.endswith('is'):
                            val_tag = child
                            break
                    cell_text = ""
                    if val_tag is not None:
                        raw_val = val_tag.text or ""
                        if cell_type == 's':
                            try:
                                idx = int(raw_val)
                                cell_text = shared_strings[idx] if idx < len(shared_strings) else raw_val
                            except (ValueError, IndexError):
                                cell_text = raw_val
                        elif cell_type == 'b':
                            cell_text = "TRUE" if raw_val == "1" else "FALSE"
                        elif val_tag.tag.endswith('is'):
                            parts = [t.text or "" for t in val_tag.iter() if t.tag.endswith('t')]
                            cell_text = "".join(parts)
                        else:
                            cell_text = raw_val
                    cell_values.append(cell_text)
            if any(cell_values):
                rows.append(cell_values)
    out = io.StringIO()
    writer = csv.writer(out)
    for r in rows:
        writer.writerow(r)
    return out.getvalue()

def parse_xlsx_sheets(xlsx_bytes: bytes) -> Dict[str, str]:
    """
    Parses all worksheets from an .xlsx archive into a dictionary:
    { "SheetName": "CSV content", ... }
    """
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as zf:
        shared_strings = _parse_shared_strings(zf)
        sheets_map: Dict[str, str] = {}
        
        # Check workbook.xml and its relationships
        wb_file = next((n for n in zf.namelist() if n.lower().endswith("workbook.xml")), None)
        rels_file = next((n for n in zf.namelist() if "workbook.xml.rels" in n.lower()), None)
        
        resolved_sheets: List[Tuple[str, str]] = []
        if wb_file and rels_file:
            try:
                wb_tree = ET.fromstring(zf.read(wb_file))
                rels_tree = ET.fromstring(zf.read(rels_file))
                rels = {}
                for r in rels_tree.iter():
                    if r.tag.endswith('Relationship') or 'Relationship' in r.tag:
                        rid = r.attrib.get('Id')
                        target = r.attrib.get('Target')
                        if rid and target:
                            # Normalize path relative to xl/
                            norm_target = posixpath.normpath(posixpath.join("xl", target)).replace("\\", "/")
                            rels[rid] = norm_target
                
                for s in wb_tree.iter():
                    if s.tag.endswith('sheet'):
                        name = s.attrib.get('name')
                        rid = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id') or s.attrib.get('id')
                        if name and rid and rid in rels:
                            resolved_sheets.append((name, rels[rid]))
            except Exception:
                pass

        if not resolved_sheets:
            # Fallback to finding all sheet XMLs directly in archive
            sheet_candidates = sorted([
                n for n in zf.namelist()
                if "worksheets/sheet" in n.lower() and n.lower().endswith(".xml")
            ])
            for idx, sc in enumerate(sheet_candidates, start=1):
                resolved_sheets.append((f"Sheet{idx}", sc))

        for sheet_name, sheet_path in resolved_sheets:
            target_path = sheet_path if sheet_path in zf.namelist() else next((n for n in zf.namelist() if n.lower() == sheet_path.lower()), None)
            if target_path:
                try:
                    ws_xml = zf.read(target_path)
                    csv_text = _parse_sheet_xml(ws_xml, shared_strings)
                    if csv_text.strip():
                        sheets_map[sheet_name] = csv_text
                except Exception:
                    pass

        return sheets_map

def parse_xlsx_to_csv_text(xlsx_bytes: bytes, sheet_name: Optional[str] = None) -> str:
    """
    Converts bytes of an .xlsx workbook into CSV-formatted text.
    If sheet_name is provided, converts that sheet; otherwise returns the first available sheet.
    """
    sheets = parse_xlsx_sheets(xlsx_bytes)
    if not sheets:
        raise ValueError("No valid worksheets with data found in XLSX file archive.")
    if sheet_name and sheet_name in sheets:
        return sheets[sheet_name]
    # Return first sheet
    return next(iter(sheets.values()))
