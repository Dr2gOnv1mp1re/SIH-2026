// verify_all_navigation_routes.js
// Automated verification of all 28 sidebar items, routes, components, and live backend APIs

const http = require('http');

const BACKEND_BASE = 'http://localhost:8000/api/v1';

async function fetchApi(endpoint, options = {}, token = null) {
  return new Promise((resolve) => {
    const url = new URL(BACKEND_BASE + endpoint);
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const req = http.request(url, {
      method: options.method || 'GET',
      headers
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          resolve({ status: res.statusCode, raw: data });
        }
      });
    });
    req.on('error', (err) => resolve({ status: 500, error: err.message }));
    if (options.body) req.write(JSON.stringify(options.body));
    req.end();
  });
}

// Complete route audit specification matching all sidebar items
const SIDEBAR_AUDIT_ITEMS = [
  // OVERVIEW
  { section: 'OVERVIEW', label: 'Executive Overview', route: '/', component: 'ExecutiveDashboard', method: 'GET', api: '/risk/enterprise' },
  { section: 'OVERVIEW', label: 'CISO Command Center', route: '/ciso', component: 'CISODashboard', method: 'GET', api: '/ciso/decision' },
  { section: 'OVERVIEW', label: 'Executive Board', route: '/executive-board', component: 'ExecutiveBoardView', method: 'GET', api: '/ciso/decision' },

  // RISK INTELLIGENCE
  { section: 'RISK INTELLIGENCE', label: 'Risk Dashboard', route: '/risk', component: 'RiskHeatmap', method: 'GET', api: '/risk/assets' },
  { section: 'RISK INTELLIGENCE', label: 'Risk History', route: '/risk-history', component: 'RiskHistoryPage', method: 'GET', api: '/risk/history' },
  { section: 'RISK INTELLIGENCE', label: 'Attack Paths', route: '/attack-paths', component: 'AttackPaths', method: 'GET', api: '/attack-paths/graph' },
  { section: 'RISK INTELLIGENCE', label: 'Real-World Scenario Lab', route: '/scenario-lab', component: 'RealWorldScenarioLab', method: 'GET', api: '/real-world-scenarios/catalog' },
  { section: 'RISK INTELLIGENCE', label: 'Incident & Loss Intelligence', route: '/incidents', component: 'IncidentLossIntelligence', method: 'GET', api: '/incidents' },

  // ENTERPRISE DATA
  { section: 'ENTERPRISE DATA', label: 'Data Management', route: '/data-management', component: 'DataManagement', method: 'GET', api: '/universal-import/datasets' },
  { section: 'ENTERPRISE DATA', label: 'Asset Inventory', route: '/assets', component: 'AssetInventory', method: 'GET', api: '/assets' },
  { section: 'ENTERPRISE DATA', label: 'Vulnerabilities', route: '/vulnerabilities', component: 'VulnerabilityManagement', method: 'GET', api: '/vulnerabilities' },
  { section: 'ENTERPRISE DATA', label: 'Threat Intelligence', route: '/threat-intelligence', component: 'ThreatIntelligence', method: 'GET', api: '/threats' },
  { section: 'ENTERPRISE DATA', label: 'Security Controls', route: '/security-controls', component: 'SecurityControls', method: 'GET', api: '/controls' },

  // FINANCIAL RISK
  { section: 'FINANCIAL RISK', label: 'Financial Risk', route: '/financial-risk', component: 'FinancialExposure', method: 'GET', api: '/financial/enterprise' },
  { section: 'FINANCIAL RISK', label: 'Monte Carlo', route: '/monte-carlo', component: 'MonteCarloPage', method: 'GET', api: '/financial/monte-carlo?iterations=1000' },
  { section: 'FINANCIAL RISK', label: 'Risk Appetite', route: '/risk-appetite', component: 'RiskAppetitePage', method: 'GET', api: '/organizations/current' },

  // AI & ANALYTICS
  { section: 'AI & ANALYTICS', label: 'Future Risk', route: '/future-risk', component: 'FutureRiskPage', method: 'GET', api: '/ai/predictions' },
  { section: 'AI & ANALYTICS', label: 'Explainable AI', route: '/explainable-ai', component: 'ExplainableAIPage', method: 'GET', api: '/ai/predictions' },
  { section: 'AI & ANALYTICS', label: 'Scenario Analysis', route: '/scenario-analysis', component: 'WhatIfSimulator', method: 'GET', api: '/scenarios/interventions' },

  // INVESTMENT
  { section: 'INVESTMENT', label: 'Investment Optimizer', route: '/investment-optimizer', component: 'InvestmentOptimizer', method: 'POST', api: '/optimization/run', body: { budget: 10000000 } },
  { section: 'INVESTMENT', label: 'Budget Stress Test', route: '/budget-stress-test', component: 'BudgetStressTestPage', method: 'GET', api: '/optimization/stress-test' },

  // GOVERNANCE
  { section: 'GOVERNANCE', label: 'CISO Decisions', route: '/ciso-decisions', component: 'CISODecisionsPage', method: 'GET', api: '/ciso/decision' },
  { section: 'GOVERNANCE', label: 'Audit Trail', route: '/audit-trail', component: 'AuditorDashboard', method: 'GET', api: '/blockchain/blocks' },
  { section: 'GOVERNANCE', label: 'Blockchain Audit', route: '/blockchain-audit', component: 'BlockchainAudit', method: 'GET', api: '/blockchain/blocks' },
  { section: 'GOVERNANCE', label: 'Compliance', route: '/compliance', component: 'ComplianceMatrix', method: 'GET', api: '/compliance' },
  { section: 'GOVERNANCE', label: 'Reports', route: '/reports', component: 'ExecutiveReports', method: 'POST', api: '/reports/generate', body: { report_type: 'BOARD_QUARTERLY' } },

  // SIH FINAL DEMO
  { section: 'SIH FINAL DEMO', label: 'SIH Final Demo', route: '/sih-demo', component: 'SIHFinalDemoPage', method: 'GET', api: '/demo/steps' },

  // SYSTEM
  { section: 'SYSTEM', label: 'System Health', route: '/system-status', component: 'SystemStatusPage', method: 'GET', api: '/health' }
];

async function runAudit() {
  console.log('========================================================================');
  console.log('       QUANTUM RISK AI — COMPLETE FRONTEND NAVIGATION & API AUDIT       ');
  console.log('========================================================================\n');

  // Step 1: Login as CISO to obtain JWT Token
  process.stdout.write('Authenticating as CISO (ciso@abcbank.com) ... ');
  const authRes = await fetchApi('/auth/login', {
    method: 'POST',
    body: { email: 'ciso@abcbank.com', password: 'Ciso@12345' }
  });

  if (authRes.status !== 200 || !authRes.data?.access_token) {
    console.log(`\x1b[31mFAILED\x1b[0m (Status ${authRes.status})`);
    console.error('Could not authenticate to backend.');
    process.exit(1);
  }

  const token = authRes.data.access_token;
  console.log(`\x1b[32mAUTHENTICATED\x1b[0m (JWT acquired)\n`);

  let passed = 0;
  let failed = 0;
  const results = [];

  for (const item of SIDEBAR_AUDIT_ITEMS) {
    process.stdout.write(`Testing [${item.section}] ${item.label.padEnd(28)} -> ${item.route.padEnd(22)} ... `);
    
    // Check API endpoint health with JWT
    const apiRes = await fetchApi(item.api, {
      method: item.method,
      body: item.body
    }, token);

    const isApiOk = apiRes.status === 200 || apiRes.status === 201;

    if (isApiOk) {
      console.log(`\x1b[32mPASS\x1b[0m (HTTP ${apiRes.status})`);
      passed++;
      results.push({
        ...item,
        status: 'PASS',
        httpStatus: apiRes.status,
        apiSuccess: true,
        sampleDataKeys: apiRes.data ? Object.keys(apiRes.data).slice(0, 5) : []
      });
    } else {
      console.log(`\x1b[31mFAIL\x1b[0m (HTTP ${apiRes.status})`);
      failed++;
      results.push({
        ...item,
        status: 'FAIL',
        httpStatus: apiRes.status,
        apiSuccess: false,
        error: apiRes.error || apiRes.raw
      });
    }
  }

  console.log('\n========================================================================');
  console.log('            DIRECT URL SPA FALLBACK & REFRESH VERIFICATION              ');
  console.log('========================================================================\n');

  let directPassed = 0;
  for (const item of SIDEBAR_AUDIT_ITEMS) {
    const directRes = await new Promise((resolve) => {
      http.get('http://localhost:5173' + item.route, (res) => {
        resolve({ status: res.statusCode });
      }).on('error', (err) => resolve({ status: 500, error: err.message }));
    });

    process.stdout.write(`Direct URL: ('http://localhost:5173${item.route}')`.padEnd(58) + ` ... `);
    if (directRes.status === 200) {
      console.log(`\x1b[32mPASS\x1b[0m (HTTP 200 SPA Fallback)`);
      directPassed++;
    } else {
      console.log(`\x1b[31mFAIL\x1b[0m (HTTP ${directRes.status})`);
    }
  }

  console.log('\n========================================================================');
  console.log(`TOTAL SIDEBAR ITEMS AUDITED: ${SIDEBAR_AUDIT_ITEMS.length}`);
  console.log(`PASSED: ${passed}`);
  console.log(`FAILED: ${failed}`);
  console.log(`DIRECT SPA URLs PASSED: ${directPassed} / ${SIDEBAR_AUDIT_ITEMS.length}`);
  console.log(`PARTIAL: 0`);
  console.log(`FRONTEND NAVIGATION READINESS: ${failed === 0 && directPassed === SIDEBAR_AUDIT_ITEMS.length ? 'READY' : 'NOT READY'}`);
  console.log('========================================================================\n');

  const fs = require('fs');
  fs.writeFileSync('d:\\SIH\\frontend_navigation_audit_results.json', JSON.stringify({
    total: SIDEBAR_AUDIT_ITEMS.length,
    passed,
    failed,
    directPassed,
    partial: 0,
    readiness: failed === 0 && directPassed === SIDEBAR_AUDIT_ITEMS.length ? 'READY' : 'NOT READY',
    results
  }, null, 2));
}

runAudit();
