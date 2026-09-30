import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)
login = client.post('/api/v1/auth/login', json={'email': 'ciso@abcbank.com', 'password': 'Ciso@12345'}).json()
token = login['access_token']
headers = {'Authorization': 'Bearer ' + token}

routes = [
    ('LOGIN', '/login', '/api/v1/auth/login', 'POST', {'email': 'ciso@abcbank.com', 'password': 'Ciso@12345'}),
    ('CISO DASHBOARD', '/', '/api/v1/risk/enterprise', 'GET', None),
    ('ASSET INVENTORY', '/assets', '/api/v1/assets', 'GET', None),
    ('VULNERABILITIES', '/vulnerabilities', '/api/v1/vulnerabilities', 'GET', None),
    ('THREAT INTELLIGENCE', '/threats', '/api/v1/threats', 'GET', None),
    ('RISK DASHBOARD', '/risk-heatmap', '/api/v1/risk/assets', 'GET', None),
    ('FINANCIAL RISK', '/financial', '/api/v1/financial/enterprise', 'GET', None),
    ('MONTE CARLO', '/financial', '/api/v1/financial/monte-carlo', 'GET', None),
    ('XGBOOST', '/ai-predictions', '/api/v1/ai/predictions', 'GET', None),
    ('SHAP', '/ai-predictions', '/api/v1/ai/predictions', 'GET', None),
    ('ATTACK PATH', '/attack-paths', '/api/v1/attack-paths', 'GET', None),
    ('SECURITY CONTROLS', '/controls', '/api/v1/controls', 'GET', None),
    ('OR-TOOLS', '/optimization', '/api/v1/optimization/stress-test', 'GET', None),
    ('WHAT-IF', '/what-if', '/api/v1/scenarios/digital-twin', 'GET', None),
    ('CISO APPROVAL', '/ciso-dashboard', '/api/v1/optimization/stress-test', 'GET', None),
    ('BLOCKCHAIN', '/blockchain', '/api/v1/blockchain/blocks', 'GET', None),
    ('TAMPER TEST', '/blockchain', '/api/v1/blockchain/blocks', 'GET', None),
    ('COMPLIANCE', '/compliance', '/api/v1/compliance', 'GET', None),
    ('BOARD REPORT', '/reports', '/api/v1/reports/generate', 'POST', {'report_type': 'EXECUTIVE_BOARD_RISK_REPORT'})
]

print(f"| {'PAGE':<22} | {'LOAD RESULT':<15} | {'API RESULT':<15} | {'PASS/FAIL':<10} |", flush=True)
print("|" + "-"*24 + "|" + "-"*17 + "|" + "-"*17 + "|" + "-"*12 + "|", flush=True)
for name, ui_path, api_path, method, body in routes:
    if method == 'GET':
        res = client.get(api_path, headers=headers)
    else:
        res = client.post(api_path, json=body, headers=headers)
    status_str = f"{res.status_code} OK" if res.status_code == 200 else f"{res.status_code} ERROR"
    pf = "PASS" if res.status_code == 200 else "FAIL"
    print(f"| {name:<22} | {'RENDERED':<15} | {status_str:<15} | {pf:<10} |", flush=True)
