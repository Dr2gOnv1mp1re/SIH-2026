import axios from 'axios';

// Dynamically align API base URL with the active frontend loopback origin (127.0.0.1 or localhost)
const getBaseApiUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (typeof window !== 'undefined' && window.location.hostname) {
    const currentHost = window.location.hostname; // '127.0.0.1' or 'localhost'
    if (envUrl) {
      try {
        const parsed = new URL(envUrl);
        // Align loopback host if either 127.0.0.1 or localhost is used
        if (
          (currentHost === '127.0.0.1' || currentHost === 'localhost') &&
          (parsed.hostname === '127.0.0.1' || parsed.hostname === 'localhost')
        ) {
          parsed.hostname = currentHost;
          return parsed.toString().replace(/\/$/, '');
        }
      } catch (e) {
        // fallback to envUrl
      }
      return envUrl;
    }
    return `http://${currentHost}:8000/api/v1`;
  }
  return envUrl || 'http://127.0.0.1:8000/api/v1';
};

const API_BASE_URL = getBaseApiUrl();

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('cyber_risk_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept errors: handle network connection errors, 401s, and provide clear error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      // Network error, backend offline, or connection refused
      console.warn(`[Quantum Risk AI Network Warning]: Backend unreachable at ${API_BASE_URL}. Ensure backend is running on port 8000.`);
      error.friendlyMessage = 'Unable to connect to Quantum Risk AI backend. Please verify backend is running on port 8000.';
    } else if (error.response.status === 401) {
      localStorage.removeItem('cyber_risk_token');
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login?expired=1';
      }
    }
    return Promise.reject(error);
  }
);

// API Service functions
export const authService = {
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },
  changePassword: async (old_password: string, new_password: string) => {
    const res = await api.post('/auth/change-password', { old_password, new_password });
    return res.data;
  },
  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  }
};

export const organizationService = {
  getCurrent: async () => {
    const res = await api.get('/organizations/current');
    return res.data;
  },
  updateCurrent: async (data: any) => {
    const res = await api.put('/organizations/current', data);
    return res.data;
  }
};

export const assetService = {
  list: async (params?: any) => {
    const res = await api.get('/assets', { params });
    return res.data;
  },
  getAll: async (params?: any) => {
    const res = await api.get('/assets', { params });
    return res.data;
  },
  get: async (id: string) => {
    const res = await api.get(`/assets/${id}`);
    return res.data;
  },
  importCSV: async (csv_content: string) => {
    const res = await api.post('/assets/import-csv', { csv_content });
    return res.data;
  },
  exportCSV: async () => {
    const res = await api.get('/assets/export-csv', { responseType: 'blob' });
    return res.data;
  },
  getTemplateCSV: async () => {
    const res = await api.get('/assets/template-csv', { responseType: 'blob' });
    return res.data;
  }
};

export const vulnerabilityService = {
  list: async (params?: any) => {
    const res = await api.get('/vulnerabilities', { params });
    return res.data;
  }
};

export const threatService = {
  list: async () => {
    const res = await api.get('/threats');
    return res.data;
  }
};

export const controlService = {
  list: async () => {
    const res = await api.get('/controls');
    return res.data;
  },
  update: async (id: string, data: any) => {
    const res = await api.put(`/controls/${id}`, data);
    return res.data;
  }
};

export const riskService = {
  getEnterpriseRisk: async () => {
    const res = await api.get('/risk/enterprise');
    return res.data;
  },
  getTopAssets: async () => {
    const res = await api.get('/risk/assets');
    return res.data;
  },
  getHistory: async () => {
    const res = await api.get('/risk/history');
    return res.data;
  },
  recalculate: async () => {
    const res = await api.post('/risk/recalculate');
    return res.data;
  }
};

export const financialService = {
  getEnterpriseExposure: async () => {
    const res = await api.get('/financial/enterprise');
    return res.data;
  },
  getMonteCarlo: async (iterations = 10000) => {
    const res = await api.get('/financial/monte-carlo', { params: { iterations } });
    return res.data;
  },
  updateAssumptions: async (data: any) => {
    const res = await api.post('/financial/assumptions', data);
    return res.data;
  }
};

export const aiService = {
  getPredictions: async () => {
    const res = await api.get('/ai/predictions');
    return res.data;
  },
  getExplanations: async () => {
    const res = await api.get('/ai/explanations');
    return res.data;
  },
  retrain: async () => {
    const res = await api.post('/ai/retrain');
    return res.data;
  }
};

export const optimizationService = {
  run: async (budget: number) => {
    const res = await api.post('/optimization/run', { budget });
    return res.data;
  },
  getStressTest: async () => {
    const res = await api.get('/optimization/stress-test');
    return res.data;
  },
  approve: async (runId: string, notes?: string) => {
    const res = await api.post('/optimization/approve', { optimization_run_id: runId, approval_notes: notes });
    return res.data;
  }
};

export const scenarioService = {
  simulate: async (params: any) => {
    const res = await api.post('/scenarios/simulate', params);
    return res.data;
  },
  getDigitalTwin: async () => {
    const res = await api.get('/scenarios/digital-twin');
    return res.data;
  },
  getInterventions: async () => {
    const res = await api.get('/scenarios/interventions');
    return res.data;
  },
  simulateControl: async (params: { intervention_id: string; custom_investment_cost?: number; custom_baseline_criticality?: number }) => {
    const res = await api.post('/scenarios/simulate-control', params);
    return res.data;
  }
};

export const attackPathService = {
  getGraph: async () => {
    const res = await api.get('/attack-paths');
    return res.data;
  }
};

export const complianceService = {
  list: async () => {
    const res = await api.get('/compliance');
    return res.data;
  },
  getGaps: async () => {
    const res = await api.get('/compliance/gaps');
    return res.data;
  }
};

export const blockchainService = {
  getBlocks: async () => {
    const res = await api.get('/blockchain/blocks');
    return res.data;
  },
  verifyRecord: async (recordId: string) => {
    const res = await api.post(`/blockchain/verify/${recordId}`);
    return res.data;
  },
  tamperTest: async (data?: any) => {
    const res = await api.post('/blockchain/tamper-test', data || {});
    return res.data;
  }
};

export const assistantService = {
  query: async (queryText: string) => {
    const res = await api.post('/assistant/query', { query: queryText });
    return res.data;
  }
};

export const integrationService = {
  getStatus: async () => {
    const res = await api.get('/integrations/status');
    return res.data;
  },
  triggerSync: async () => {
    const res = await api.post('/integrations/trigger-sync');
    return res.data;
  }
};

export const reportService = {
  generate: async (reportType: string) => {
    const res = await api.post('/reports/generate', { report_type: reportType });
    return res.data;
  }
};

export const demoService = {
  getSteps: async () => {
    const res = await api.get('/demo/steps');
    return res.data;
  },
  executeStep: async (stepNumber: number) => {
    const res = await api.post(`/demo/step/${stepNumber}`);
    return res.data;
  },
  resetDemo: async () => {
    const res = await api.post('/demo/reset');
    return res.data;
  }
};

export const cisoService = {
  getDecisionContext: async () => {
    const res = await api.get('/ciso/decision');
    return res.data;
  },
  approve: async (data: { optimization_run_id?: string; decision_notes?: string }) => {
    const res = await api.post('/ciso/approve', data);
    return res.data;
  },
  reject: async (data: { optimization_run_id?: string; reason?: string }) => {
    const res = await api.post('/ciso/reject', data);
    return res.data;
  },
  requestReview: async (data: { optimization_run_id?: string; requested_changes?: string }) => {
    const res = await api.post('/ciso/request-review', data);
    return res.data;
  }
};

export const predictionService = {
  train: async () => {
    const res = await api.post('/prediction/train');
    return res.data;
  },
  predict: async (data?: any) => {
    const res = await api.post('/prediction/predict', data || {});
    return res.data;
  },
  getLatest: async () => {
    const res = await api.get('/prediction/latest');
    return res.data;
  },
  getShap: async () => {
    const res = await api.get('/prediction/shap');
    return res.data;
  }
};

export const systemService = {
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },
  getBlockchainStatus: async () => {
    const res = await api.get('/blockchain/status');
    return res.data;
  }
};

export const realWorldScenarioService = {
  getCatalog: async () => {
    const res = await api.get('/real-world-scenarios/catalog');
    return res.data;
  },
  getScenarioDetails: async (cveId: string) => {
    const res = await api.get(`/real-world-scenarios/catalog/${cveId}`);
    return res.data;
  },
  getEnterpriseProfile: async () => {
    const res = await api.get('/real-world-scenarios/enterprise-profile');
    return res.data;
  },
  analyzeScenario: async (payload: {
    cve_id?: string;
    selected_asset_name?: string;
    selected_business_service?: string;
    enterprise_overrides?: Record<string, any>;
  }) => {
    const res = await api.post('/real-world-scenarios/analyze', payload);
    return res.data;
  },
  runWhatIf: async (payload: {
    cve_id?: string;
    enterprise_overrides?: Record<string, any>;
  }) => {
    const res = await api.post('/real-world-scenarios/what-if', payload);
    return res.data;
  },
  optimizeInvestment: async (payload: {
    cve_id?: string;
    budget?: number;
    enterprise_overrides?: Record<string, any>;
  }) => {
    const res = await api.post('/real-world-scenarios/optimize', payload);
    return res.data;
  },
  recordCISODecision: async (payload: {
    cve_id: string;
    decision: 'APPROVE' | 'REJECT' | 'REQUEST_REVIEW';
    ciso_name?: string;
    decision_notes?: string;
    modeled_eal?: number;
    recommended_investment?: number;
    recommended_controls?: string[];
    requested_changes?: string;
  }) => {
    const res = await api.post('/real-world-scenarios/ciso-decision', payload);
    return res.data;
  },
  getHistory: async () => {
    const res = await api.get('/real-world-scenarios/history');
    return res.data;
  }
};

export const provenanceService = {
  getAll: async () => {
    const res = await api.get('/provenance');
    return res.data;
  },
  getByCategory: async (cat: string) => {
    const res = await api.get(`/provenance/category/${cat}`);
    return res.data;
  }
};

export const incidentService = {
  getAll: async (params?: Record<string, any>) => {
    const res = await api.get('/incidents', { params });
    return res.data;
  },
  getStatistics: async () => {
    const res = await api.get('/incidents/statistics');
    return res.data;
  },
  getLossSummary: async () => {
    const res = await api.get('/incidents/loss-summary');
    return res.data;
  },
  getTrends: async () => {
    const res = await api.get('/incidents/trends');
    return res.data;
  },
  getDataQuality: async () => {
    const res = await api.get('/incidents/data-quality');
    return res.data;
  },
  getCalibration: async () => {
    const res = await api.get('/incidents/calibration');
    return res.data;
  },
  calibrate: async (payload: { notes?: string; apply_to_eal?: boolean }) => {
    const res = await api.post('/incidents/calibrate', payload);
    return res.data;
  },
  getDetail: async (id: string) => {
    const res = await api.get(`/incidents/${id}`);
    return res.data;
  },
  create: async (payload: any) => {
    const res = await api.post('/incidents', payload);
    return res.data;
  },
  update: async (id: string, payload: any) => {
    const res = await api.put(`/incidents/${id}`, payload);
    return res.data;
  },
  delete: async (id: string) => {
    const res = await api.delete(`/incidents/${id}`);
    return res.data;
  },
  importCsv: async (file: File, dryRun: boolean = false) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post(`/incidents/import-csv?dry_run=${dryRun}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return res.data;
  }
};

export const sihDatasetService = {
  getOverview: async () => {
    const res = await api.get('/sih-dataset/overview');
    return res.data;
  },
  getAssets: async () => {
    const res = await api.get('/sih-dataset/assets');
    return res.data;
  },
  getVulnerabilities: async () => {
    const res = await api.get('/sih-dataset/vulnerabilities');
    return res.data;
  },
  getThreatIntel: async () => {
    const res = await api.get('/sih-dataset/threat-intelligence');
    return res.data;
  },
  getSiemEvents: async () => {
    const res = await api.get('/sih-dataset/siem-events');
    return res.data;
  },
  getIamAnalysis: async () => {
    const res = await api.get('/sih-dataset/iam-analysis');
    return res.data;
  },
  getEdrTelemetry: async () => {
    const res = await api.get('/sih-dataset/edr-telemetry');
    return res.data;
  },
  getCspmFindings: async () => {
    const res = await api.get('/sih-dataset/cspm-findings');
    return res.data;
  },
  getFinancialRisk: async () => {
    const res = await api.get('/sih-dataset/financial-risk');
    return res.data;
  },
  getMonteCarlo: async (iterations: number = 10000) => {
    const res = await api.get('/sih-dataset/monte-carlo', { params: { iterations } });
    return res.data;
  },
  optimize: async (budget: number = 1500000) => {
    const res = await api.post('/sih-dataset/optimize', { budget });
    return res.data;
  },
  getAttackPaths: async () => {
    const res = await api.get('/sih-dataset/attack-paths');
    return res.data;
  },
  getFutureRisk: async () => {
    const res = await api.get('/sih-dataset/future-risk');
    return res.data;
  },
  getCiso: async () => {
    const res = await api.get('/sih-dataset/ciso');
    return res.data;
  },
  importCsv: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/sih-dataset/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  }
};

export const universalImportService = {
  detectMappings: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/universal-import/detect-mappings', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  analyzeRaw: async (csv_content: string, filename: string = 'dataset.csv') => {
    const res = await api.post('/universal-import/analyze-raw', { csv_content, filename });
    return res.data;
  },
  executeImport: async (payload: {
    file?: File;
    csv_content?: string;
    filename?: string;
    custom_mappings?: Record<string, string>;
    duplicate_strategy?: string;
  }) => {
    if (payload.file) {
      const formData = new FormData();
      formData.append('file', payload.file);
      if (payload.filename) formData.append('filename', payload.filename);
      if (payload.custom_mappings) {
        formData.append('custom_mappings_json', JSON.stringify(payload.custom_mappings));
      }
      formData.append('duplicate_strategy', payload.duplicate_strategy || 'update_existing');
      const res = await api.post('/universal-import/execute', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return res.data;
    } else {
      const res = await api.post('/universal-import/execute-json', {
        csv_content: payload.csv_content || '',
        filename: payload.filename || 'dataset.csv',
        custom_mappings: payload.custom_mappings,
        duplicate_strategy: payload.duplicate_strategy || 'update_existing'
      });
      return res.data;
    }
  },
  detectPackage: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/universal-import/detect-package', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  executePackage: async (file: File, duplicate_strategy: string = 'update_existing', dataset_id?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('duplicate_strategy', duplicate_strategy);
    if (dataset_id) formData.append('dataset_id', dataset_id);
    const res = await api.post('/universal-import/execute-package', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  getActive: async () => {
    const res = await api.get('/universal-import/active');
    return res.data;
  },
  getOverview: async () => {
    const res = await api.get('/universal-import/overview');
    return res.data;
  },
  getAssets: async () => {
    const res = await api.get('/universal-import/assets');
    return res.data;
  },
  getVulnerabilities: async () => {
    const res = await api.get('/universal-import/vulnerabilities');
    return res.data;
  },
  getDatasets: async () => {
    const res = await api.get('/universal-import/datasets');
    return res.data;
  },
  selectDataset: async (filename: string) => {
    const res = await api.post('/universal-import/select-dataset', null, {
      params: { filename }
    });
    return res.data;
  }
};

export const demoWorkflowService = {
  getSteps: async () => {
    const res = await api.get('/demo/steps');
    return res.data;
  },
  activateStep: async (step_number: number) => {
    const res = await api.post(`/demo/step/${step_number}`);
    return res.data;
  },
  resetDemo: async () => {
    const res = await api.post('/demo/reset');
    return res.data;
  }
};



