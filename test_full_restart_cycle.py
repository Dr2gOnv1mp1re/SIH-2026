import subprocess
import time
import urllib.request
import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

def kill_ports():
    """Kills any process running on ports 8000 or 5173."""
    ps_cmd = (
        "$ports = @(8000, 5173); foreach ($port in $ports) { "
        "$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue; "
        "if ($connections) { $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique; "
        "foreach ($p in $pids) { try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {} } } }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)

def start_services():
    """Starts backend and frontend using run_background.ps1."""
    run_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_background.ps1")
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", run_script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_for_backend(timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"{BACKEND_URL}/health", headers={"User-Agent": "HealthChecker"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    if data.get("status") == "ok":
                        return True
        except Exception:
            time.sleep(0.5)
    return False

def wait_for_frontend(timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(FRONTEND_URL, headers={"User-Agent": "HealthChecker"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def api_call(path, method="GET", body=None, token=None):
    url = f"{BACKEND_URL}/api/v1{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, str(e)
    except Exception as e:
        return 500, str(e)

def test_single_cycle(run_num):
    print(f"\n========================================================")
    print(f"             EXECUTING RESTART TEST: RUN {run_num}")
    print(f"========================================================")
    
    # 1. Kill stale processes
    print(f"[Run {run_num}] Stopping any active processes on ports 8000 & 5173...")
    kill_ports()
    
    # 2. Start services
    print(f"[Run {run_num}] Starting Quantum Risk AI platform...")
    start_services()
    
    # 3. Wait for Backend
    print(f"[Run {run_num}] Probing backend health check at {BACKEND_URL}/health...")
    if not wait_for_backend(20):
        print(f"[Run {run_num}] FAIL: Backend failed to start within 20s.")
        return False
    print(f"[Run {run_num}] Backend healthy (HTTP 200)!")

    # 4. Wait for Frontend
    print(f"[Run {run_num}] Probing frontend SPA at {FRONTEND_URL}...")
    if not wait_for_frontend(20):
        print(f"[Run {run_num}] FAIL: Frontend failed to start within 20s.")
        return False
    print(f"[Run {run_num}] Frontend responsive (HTTP 200)!")

    # 5. Authenticate
    status, auth_data = api_call("/auth/login", method="POST", body={"email": "ciso@abcbank.com", "password": "Ciso@12345"})
    if status != 200 or "access_token" not in auth_data:
        print(f"[Run {run_num}] FAIL: Authentication failed (Status {status}).")
        return False
    token = auth_data["access_token"]
    print(f"[Run {run_num}] Authenticated as CISO (JWT acquired).")

    # 6. Verify Critical Pages / APIs
    critical_checks = [
        ("Dashboard (Overview)", "/risk/enterprise", "GET", None),
        ("Assets Inventory", "/assets", "GET", None),
        ("Vulnerabilities", "/vulnerabilities", "GET", None),
        ("Monte Carlo", "/financial/monte-carlo?iterations=1000", "GET", None),
        ("Future Risk", "/ai/predictions", "GET", None),
        ("Investment Optimizer", "/optimization/run", "POST", {"budget": 10000000}),
        ("CISO Decisions", "/ciso/decision", "GET", None),
        ("Blockchain Audit", "/blockchain/blocks", "GET", None),
        ("Reports", "/reports/generate", "POST", {"report_type": "BOARD_QUARTERLY"}),
        ("SIH Final Demo", "/demo/steps", "GET", None)
    ]

    all_ok = True
    for label, path, method, payload in critical_checks:
        st, res = api_call(path, method=method, body=payload, token=token)
        if st in (200, 201):
            print(f"  [PASS] {label.ljust(25)} -> HTTP {st}")
        else:
            print(f"  [FAIL] {label.ljust(25)} -> HTTP {st}")
            all_ok = False

    if all_ok:
        print(f"\n>>> RUN {run_num} RESULT: PASS <<<")
        return True
    else:
        print(f"\n>>> RUN {run_num} RESULT: FAIL <<<")
        return False

def main():
    print("QUANTUM RISK AI — 5-RUN CLEAN START & RESTART VALIDATION SUITE")
    results = {}
    for i in range(1, 6):
        ok = test_single_cycle(i)
        results[f"RUN_{i}"] = "PASS" if ok else "FAIL"
        time.sleep(1.5)

    print("\n========================================================")
    print("               FINAL RESTART TEST SUMMARY               ")
    print("========================================================")
    for k, v in results.items():
        print(f"  {k} -> {v}")
    
    all_pass = all(v == "PASS" for v in results.values())
    print(f"\nOVERALL RESTART READINESS: {'READY' if all_pass else 'NOT READY'}")
    print("========================================================\n")
    
    with open("restart_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()
