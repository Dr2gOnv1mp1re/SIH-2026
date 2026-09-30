# Quantum Risk AI — Deployment & Production Architecture Guide

**Platform:** AI-Powered Continuous Cyber Risk Quantification & Investment Optimization Platform  
**Architecture:** Decoupled Full-Stack Architecture (React + Vite SPA Frontend & FastAPI Asynchronous Risk Engine Backend)

---

## 1. Project Structure

The project is structured as a decoupled monorepo:

```text
SIH/
├── backend/                              # Python 3.10+ FastAPI Risk & ML Engine
│   ├── app/
│   │   ├── ai_engine/                    # XGBoost, SHAP & predictive modeling
│   │   ├── api/                          # FastAPI REST endpoints (/api/v1)
│   │   ├── attack_paths/                 # Multi-hop attack path graph analyzer
│   │   ├── blockchain/                   # SHA-256 canonical audit ledger
│   │   ├── database/                     # SQLAlchemy database models & session
│   │   ├── risk_engine/                  # FAIR model, Monte Carlo & loss magnitude
│   │   └── main.py                       # FastAPI application entrypoint
│   ├── tests/                            # Pytest test suite (166 tests)
│   ├── requirements.txt                  # Python dependencies
│   └── cyber_risk_enterprise.db          # SQLite baseline enterprise database
├── frontend/                             # React 19 + TypeScript + Vite SPA
│   ├── public/
│   │   ├── _redirects                    # Netlify SPA redirect (/* /index.html 200)
│   │   ├── favicon.svg
│   │   └── icons.svg
│   ├── src/
│   │   ├── components/                   # Reusable UI components & charts
│   │   ├── context/                      # Auth, Dataset & Theme context
│   │   ├── pages/                        # 28 Enterprise & CISO view pages
│   │   ├── services/                     # Centralized Axios API service layer
│   │   └── main.tsx                      # Frontend application entrypoint
│   ├── dist/                             # Compiled production bundle
│   ├── netlify.toml                      # Netlify configuration (Frontend directory)
│   ├── package.json                      # Frontend dependencies & scripts
│   ├── tsconfig.json                     # TypeScript compiler configuration
│   └── vite.config.ts                    # Vite build & local proxy configuration
├── netlify.toml                          # Master Netlify configuration (Monorepo root)
├── package.json                          # Root orchestration package
├── PS26105_Cyber_Risk_Test_Data.csv      # SIH ground-truth cyber risk dataset
└── DEPLOYMENT.md                         # Production deployment guide
```

---

## 2. Frontend Location
- **Directory:** `frontend/`
- **Framework:** React 19, TypeScript, Tailwind CSS, Recharts, Vite
- **Configuration:** `frontend/vite.config.ts`, `frontend/tsconfig.json`

## 3. Backend Location
- **Directory:** `backend/`
- **Framework:** Python FastAPI, SQLAlchemy, Google OR-Tools, XGBoost, SHAP, NumPy, SciPy
- **Entrypoint:** `backend/app/main.py` (`app.main:app`)

---

## 4. Local Development Commands

### Starting the Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API URL:** `http://127.0.0.1:8000/api/v1`
- **Health Check:** `http://127.0.0.1:8000/health`
- **API Swagger Docs:** `http://127.0.0.1:8000/docs`

### Starting the Frontend
```bash
cd frontend
npm install
npm run dev
```
- **Frontend Dashboard URL:** `http://127.0.0.1:5173`
- **SIH Demo Hub:** `http://127.0.0.1:5173/sih-demo`

### Master Single-Command Launch (Windows PowerShell)
```powershell
.\run_all.ps1
```

---

## 5. Build Command
To build the frontend bundle for production:

From the `frontend/` folder:
```bash
npm run build
```
Or from the project root:
```bash
npm run build
# (Runs: npm --prefix frontend run build)
```

The build compiles into `frontend/dist/`:
- `dist/index.html` (Application HTML)
- `dist/assets/` (Minified JS and CSS bundles)
- `dist/_redirects` (Netlify SPA routing rules)

---

## 6. Netlify Settings

### Option A: Monorepo Root Deployment (Recommended)
When linking the repository directly to Netlify from the root directory:

| Setting | Value |
| :--- | :--- |
| **Repository** | Connected Git repository containing the full workspace |
| **Branch** | `main` (or active development branch) |
| **Base directory** | `frontend` *(or leave blank because root `netlify.toml` specifies `base = "frontend"`)* |
| **Build command** | `npm run build` |
| **Publish directory** | `dist` *(or `frontend/dist` if Base directory is blank)* |

### Option B: Subdirectory Deployment (`frontend`)
If you specify `frontend` as the **Base directory** in the Netlify Web UI:

| Setting | Value |
| :--- | :--- |
| **Base directory** | `frontend` |
| **Build command** | `npm run build` |
| **Publish directory** | `dist` |

---

## 7. Environment Variables

Configure these in Netlify under **Site configuration > Environment variables**:

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| `NODE_VERSION` | Node.js runtime version | `20` |
| `VITE_API_BASE_URL` | Production URL of your deployed FastAPI backend | `https://your-backend-api.onrender.com/api/v1` |
| `VITE_API_URL` | Alternative alias for the API backend URL | `https://your-backend-api.onrender.com/api/v1` |
| `VITE_APP_TITLE` | Application branding | `Quantum Risk AI` |

> **Important:** Never place production secrets, database credentials, or private keys in the frontend environment variables. All variables starting with `VITE_` are publicly embedded into the client-side JavaScript.

---

## 8. SPA Routing Configuration

Quantum Risk AI uses client-side routing (`react-router-dom`) across 28 distinct views. Without SPA routing, visiting `/ciso` or refreshing `/sih-demo` on Netlify causes a `404 Not Found`.

This is solved in two redundant layers:
1. **`frontend/public/_redirects`**:
   ```text
   /*    /index.html   200
   ```
   *(Vite automatically copies this file into `dist/_redirects` upon build)*.
2. **`netlify.toml`**:
   ```toml
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

---

## 9. Backend Deployment Requirement

> [!WARNING]
> **Netlify hosts static frontends and serverless functions; it DOES NOT run Python FastAPI with SQLAlchemy, OR-Tools, XGBoost, and SQLite.**

To have a fully live production system:
1. Deploy the `backend/` directory to a Python-compatible cloud host such as:
   - **Render** (`render.yaml` or Web Service: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
   - **Railway** (Docker or Python Procfile: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
   - **Fly.io** (`fly launch` using the included `Dockerfile.backend`)
   - **AWS EC2 / DigitalOcean Droplet** / **Azure App Service**
2. Copy your backend production URL (e.g. `https://quantum-risk-backend.onrender.com/api/v1`).
3. Set `VITE_API_BASE_URL` in your Netlify site settings to point to your deployed backend.

---

## 10. Production API Configuration

The frontend API client ([`frontend/src/services/api.ts`](file:///d:/SIH/frontend/src/services/api.ts)) dynamically detects its environment:
- When running locally, it communicates with `http://localhost:8000/api/v1` or `http://127.0.0.1:8000/api/v1`.
- When deployed on Netlify, it uses `VITE_API_BASE_URL` (or `VITE_API_URL`).
- All requests automatically append JWT Bearer tokens and handle 401 session expiration cleanly.

---

## 11. Troubleshooting & Diagnosis

### Why did Netlify show "The workspace contains no project files... only .netlify/netlify-agent-runner-context.md"?
1. **Empty Git Repository:** The remote Git repository connected to Netlify was newly created or empty, and local files from `d:\SIH` had not been initialized, committed, and pushed to GitHub/GitLab.
2. **Subdirectory Misconfiguration:** The frontend code lives in `frontend/`. If Netlify checked the root without `netlify.toml` or without `base = "frontend"` configured, it could not find a standard frontend build pipeline.
3. **Missing `netlify.toml` and `_redirects`:** Netlify had no build definition or SPA rewrite rules.

---

## 12. Common Netlify Errors and Fixes

### Error 1: "Page Not Found / 404" on browser refresh
- **Cause:** Missing SPA redirect rule.
- **Fix:** Ensure `frontend/public/_redirects` exists with `/* /index.html 200` and `netlify.toml` contains `[[redirects]]`.

### Error 2: "Command 'npm run build' failed with exit code 1"
- **Cause:** TypeScript compilation error or Node version mismatch.
- **Fix:** Set `NODE_VERSION = "20"` in Netlify environment variables. Test locally with `npm run build` inside `frontend/`.

### Error 3: "Failed to load resource: net::ERR_CONNECTION_REFUSED" or CORS errors
- **Cause:** Frontend is deployed on Netlify, but `VITE_API_BASE_URL` is pointing to `http://localhost:8000` instead of a public backend URL, or the backend CORS does not permit the Netlify domain.
- **Fix:** Set `VITE_API_BASE_URL` in Netlify to your live backend URL, and ensure backend `CORS_ORIGINS` in `backend/app/core/config.py` allows your Netlify domain.
