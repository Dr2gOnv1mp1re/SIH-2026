import zipfile
import io
from app.risk_engine.xlsx_parser import parse_xlsx_to_csv_text

def test_parse_xlsx_to_csv():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr(
            'xl/sharedStrings.xml',
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<si><t>asset_id</t></si>'
            '<si><t>hostname</t></si>'
            '<si><t>AST-001</t></si>'
            '<si><t>srv-pay-01</t></si>'
            '</sst>'
        )
        zf.writestr(
            'xl/worksheets/sheet1.xml',
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData>'
            '<row><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
            '<row><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>'
            '</sheetData>'
            '</worksheet>'
        )
    csv_res = parse_xlsx_to_csv_text(buf.getvalue())
    assert "asset_id,hostname" in csv_res
    assert "AST-001,srv-pay-01" in csv_res
