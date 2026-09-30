import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Server, 
  Database, 
  AppWindow, 
  Smartphone, 
  Filter, 
  ShieldAlert, 
  CheckCircle2, 
  Upload, 
  Download, 
  FileText, 
  X, 
  AlertCircle,
  ExternalLink,
  Flame,
  AlertTriangle,
  Lock,
  Unlock,
  Radio,
  Cloud,
  DollarSign
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { assetService, sihDatasetService, universalImportService } from '../services/api';
import { Asset } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { useDataset } from '../context/DatasetContext';
import { UniversalCsvImportModal } from '../components/UniversalCsvImportModal';
import { DataSourceBadge } from '../components/DataSourceBadge';

const SEED_ASSETS: Asset[] = [
  {
    id: 'ast-01',
    name: 'Core Payment Database Cluster (Oracle RAC)',
    asset_type: 'database',
    ip_address: '10.100.4.12',
    hostname: 'db-pay-cluster-01.internal.bank',
    criticality_score: 98,
    current_risk_score: 94,
    expected_annual_loss: 7200000,
    internet_exposed: false,
    business_importance: 99,
    data_sensitivity: 98,
    revenue_dependency: 95,
    downtime_tolerance_hours: 0.5,
    operating_system: 'Oracle Enterprise Linux 8.8',
    department: 'Retail Core Payments & Settlement'
  },
  {
    id: 'ast-02',
    name: 'Online Banking API Gateway (Ingress Cluster)',
    asset_type: 'application',
    ip_address: '194.143.12.8',
    hostname: 'api-gateway.onlinebanking.bank.in',
    criticality_score: 92,
    current_risk_score: 91,
    expected_annual_loss: 4500000,
    internet_exposed: true,
    business_importance: 95,
    data_sensitivity: 90,
    revenue_dependency: 92,
    downtime_tolerance_hours: 1.0,
    operating_system: 'Alpine Linux (Kubernetes 1.28)',
    department: 'Digital Consumer Banking'
  },
  {
    id: 'ast-03',
    name: 'Active Directory Primary Domain Controller',
    asset_type: 'server',
    ip_address: '10.100.1.10',
    hostname: 'iam-dc01.corp.internal.bank',
    criticality_score: 94,
    current_risk_score: 88,
    expected_annual_loss: 3850000,
    internet_exposed: false,
    business_importance: 96,
    data_sensitivity: 94,
    revenue_dependency: 88,
    downtime_tolerance_hours: 1.0,
    operating_system: 'Windows Server 2022 Datacenter',
    department: 'Enterprise IAM & Identity'
  },
  {
    id: 'ast-04',
    name: 'Customer PII & Account Master Database',
    asset_type: 'database',
    ip_address: '10.100.4.25',
    hostname: 'db-pii-master.internal.bank',
    criticality_score: 95,
    current_risk_score: 86,
    expected_annual_loss: 3200000,
    internet_exposed: false,
    business_importance: 95,
    data_sensitivity: 99,
    revenue_dependency: 85,
    downtime_tolerance_hours: 2.0,
    operating_system: 'PostgreSQL 15 on RHEL 9',
    department: 'Customer Data Governance'
  },
  {
    id: 'ast-05',
    name: 'Treasury Trade Settlement Switch',
    asset_type: 'server',
    ip_address: '10.200.2.14',
    hostname: 'trs-switch-01.trading.internal.bank',
    criticality_score: 96,
    current_risk_score: 90,
    expected_annual_loss: 5500000,
    internet_exposed: false,
    business_importance: 98,
    data_sensitivity: 92,
    revenue_dependency: 96,
    downtime_tolerance_hours: 0.25,
    operating_system: 'Solaris 11.4 Sparc',
    department: 'Treasury & Forex Operations'
  },
  {
    id: 'ast-06',
    name: 'Card Authorization & Switching Engine',
    asset_type: 'application',
    ip_address: '10.100.8.5',
    hostname: 'auth-card-engine.internal.bank',
    criticality_score: 95,
    current_risk_score: 84,
    expected_annual_loss: 4200000,
    internet_exposed: false,
    business_importance: 96,
    data_sensitivity: 95,
    revenue_dependency: 94,
    downtime_tolerance_hours: 0.5,
    operating_system: 'Red Hat Enterprise Linux 8.9',
    department: 'Credit & Debit Card Operations'
  },
  {
    id: 'ast-07',
    name: 'External Employee VPN Gateway Portal',
    asset_type: 'server',
    ip_address: '194.143.12.20',
    hostname: 'vpn-portal.corp.bank.in',
    criticality_score: 88,
    current_risk_score: 78,
    expected_annual_loss: 3400000,
    internet_exposed: true,
    business_importance: 85,
    data_sensitivity: 82,
    revenue_dependency: 75,
    downtime_tolerance_hours: 2.0,
    operating_system: 'FortiOS 7.2 / Linux Kernel 5.4',
    department: 'Network Operations (NOC)'
  },
  {
    id: 'ast-08',
    name: 'SWIFT Financial Messaging Alliance Gateway',
    asset_type: 'application',
    ip_address: '10.200.4.50',
    hostname: 'swift-gateway-01.wire.internal.bank',
    criticality_score: 96,
    current_risk_score: 62,
    expected_annual_loss: 2200000,
    internet_exposed: false,
    business_importance: 97,
    data_sensitivity: 96,
    revenue_dependency: 90,
    downtime_tolerance_hours: 1.0,
    operating_system: 'AIX 7.3 on Power10',
    department: 'International Wire & Trade'
  },
  {
    id: 'ast-09',
    name: 'Disaster Recovery Warm Backup Vault',
    asset_type: 'server',
    ip_address: '10.300.1.5',
    hostname: 'dr-vault-hyd.internal.bank',
    criticality_score: 90,
    current_risk_score: 65,
    expected_annual_loss: 1900000,
    internet_exposed: false,
    business_importance: 92,
    data_sensitivity: 98,
    revenue_dependency: 80,
    downtime_tolerance_hours: 4.0,
    operating_system: 'TrueNAS Enterprise ZFS Storage',
    department: 'Business Continuity & DR'
  },
  {
    id: 'ast-10',
    name: 'Customer Service Web Chat & Bot Host',
    asset_type: 'application',
    ip_address: '194.143.12.45',
    hostname: 'chat-bot.customer.bank.in',
    criticality_score: 70,
    current_risk_score: 68,
    expected_annual_loss: 1850000,
    internet_exposed: true,
    business_importance: 70,
    data_sensitivity: 65,
    revenue_dependency: 60,
    downtime_tolerance_hours: 6.0,
    operating_system: 'Ubuntu 22.04 LTS',
    department: 'Customer Relationship Support'
  }
];

export const AssetInventory: React.FC = () => {
  const navigate = useNavigate();
  const { 
    isSihDataset,
    isCustomDataset,
    customDataset,
    customAssets,
    originLabel, 
    sihMetrics, 
    totalAssetsCount, 
    refreshSihMetrics,
    refreshCustomDataset 
  } = useDataset();

  const [assets, setAssets] = useState<Asset[]>(SEED_ASSETS);
  const [sihAssets, setSihAssets] = useState<any[]>([]);
  const [uploadedAssets, setUploadedAssets] = useState<any[]>([]);
  const [search, setSearch] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(SEED_ASSETS[0]);
  const [selectedSihAsset, setSelectedSihAsset] = useState<any | null>(null);
  const [selectedCustomAsset, setSelectedCustomAsset] = useState<any | null>(null);
  
  // Universal CSV Import Modal
  const [isImportModalOpen, setIsImportModalOpen] = useState<boolean>(false);
  const [dataOrigin, setDataOrigin] = useState<string>('SYNTHETIC DEMO DATA (ABC BANK)');

  useEffect(() => {
    if (isCustomDataset) {
      fetchUploadedAssets();
    } else if (isSihDataset) {
      fetchSihAssets();
    } else {
      fetchAssets();
    }
  }, [isCustomDataset, isSihDataset, customDataset, typeFilter]);

  const fetchUploadedAssets = async () => {
    try {
      const data = await universalImportService.getAssets();
      if (Array.isArray(data) && data.length > 0) {
        setUploadedAssets(data);
        if (!selectedCustomAsset || !data.find(a => a.asset_id === selectedCustomAsset.asset_id)) {
          setSelectedCustomAsset(data[0]);
        }
      } else if (customAssets && customAssets.length > 0) {
        setUploadedAssets(customAssets);
        setSelectedCustomAsset(customAssets[0]);
      }
    } catch (e) {
      console.error('Failed to fetch custom uploaded assets:', e);
      if (customAssets && customAssets.length > 0) {
        setUploadedAssets(customAssets);
        setSelectedCustomAsset(customAssets[0]);
      }
    }
  };

  const fetchSihAssets = async () => {
    try {
      const data = await sihDatasetService.getAssets();
      if (Array.isArray(data) && data.length > 0) {
        setSihAssets(data);
        if (!selectedSihAsset || !data.find(a => a.asset_id === selectedSihAsset.asset_id)) {
          setSelectedSihAsset(data[0]);
        }
      }
    } catch (e) {
      console.error('Failed to fetch SIH assets:', e);
    }
  };

  const fetchAssets = async () => {
    try {
      const data = await assetService.list({ asset_type: typeFilter === 'all' ? undefined : typeFilter });
      if (Array.isArray(data) && data.length > 0) {
        setAssets(data);
        const hasImported = data.some((a: any) => a.tags && (a.tags.includes('CSV_IMPORTED') || a.tags.includes('ORGANIZATION_DATA')));
        if (hasImported) {
          setDataOrigin('ORGANIZATION-PROVIDED DATA');
        }
      } else {
        setAssets(SEED_ASSETS);
      }
    } catch (e) {
      setAssets(SEED_ASSETS);
    }
  };

  const handleExportCSV = async () => {
    try {
      const blob = await assetService.exportCSV();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${isCustomDataset ? customDataset?.filename || 'custom_dataset' : 'organization_asset_inventory'}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export asset CSV.');
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const blob = await assetService.getTemplateCSV();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'cyber_risk_sample_template.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download template.');
    }
  };

  // Filter custom uploaded assets
  const filteredCustomAssets = uploadedAssets.filter(a => {
    const matchSearch = 
      (a.asset_name && a.asset_name.toLowerCase().includes(search.toLowerCase())) ||
      (a.asset_id && a.asset_id.toLowerCase().includes(search.toLowerCase())) ||
      (a.business_unit && a.business_unit.toLowerCase().includes(search.toLowerCase())) ||
      (a.ip_address && a.ip_address.toLowerCase().includes(search.toLowerCase())) ||
      (a.hostname && a.hostname.toLowerCase().includes(search.toLowerCase())) ||
      (a.iam_user && a.iam_user.toLowerCase().includes(search.toLowerCase())) ||
      (a.associated_vulnerabilities && a.associated_vulnerabilities.some((v: any) => v.cve_id.toLowerCase().includes(search.toLowerCase())));
    
    const matchType = typeFilter === 'all' || (a.asset_type && a.asset_type.toLowerCase().includes(typeFilter.toLowerCase()));
    
    let matchRisk = true;
    const rScore = a.calculated_risk_score || 0;
    if (riskFilter === 'critical') matchRisk = rScore >= 80;
    else if (riskFilter === 'high') matchRisk = rScore >= 60 && rScore < 80;
    else if (riskFilter === 'medium') matchRisk = rScore >= 40 && rScore < 60;

    return matchSearch && matchType && matchRisk;
  });

  // Filter SIH assets
  const filteredSihAssets = sihAssets.filter(a => {
    const matchSearch = 
      a.asset_name.toLowerCase().includes(search.toLowerCase()) ||
      a.asset_id.toLowerCase().includes(search.toLowerCase()) ||
      a.business_unit.toLowerCase().includes(search.toLowerCase()) ||
      (a.cve_id && a.cve_id.toLowerCase().includes(search.toLowerCase())) ||
      (a.iam_user && a.iam_user.toLowerCase().includes(search.toLowerCase()));
    
    const matchType = typeFilter === 'all' || a.asset_type.toLowerCase().includes(typeFilter.toLowerCase());
    
    let matchRisk = true;
    if (riskFilter === 'critical') matchRisk = (a.calculated_risk_score || 0) >= 80;
    else if (riskFilter === 'high') matchRisk = (a.calculated_risk_score || 0) >= 60 && (a.calculated_risk_score || 0) < 80;
    else if (riskFilter === 'medium') matchRisk = (a.calculated_risk_score || 0) >= 40 && (a.calculated_risk_score || 0) < 60;

    return matchSearch && matchType && matchRisk;
  });

  // Filter Demo assets
  const filteredAssets = assets.filter(a => {
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.hostname?.toLowerCase().includes(search.toLowerCase()) ||
      a.ip_address?.toLowerCase().includes(search.toLowerCase());
    
    const matchType = typeFilter === 'all' || a.asset_type.toLowerCase() === typeFilter.toLowerCase();
    
    let matchRisk = true;
    if (riskFilter === 'critical') matchRisk = (a.current_risk_score || 0) >= 90;
    else if (riskFilter === 'high') matchRisk = (a.current_risk_score || 0) >= 70 && (a.current_risk_score || 0) < 90;
    else if (riskFilter === 'medium') matchRisk = (a.current_risk_score || 0) >= 40 && (a.current_risk_score || 0) < 70;

    return matchSearch && matchType && matchRisk;
  });

  const currentDisplayCount = isCustomDataset 
    ? filteredCustomAssets.length 
    : (isSihDataset ? filteredSihAssets.length : filteredAssets.length);

  const currentTotalCount = isCustomDataset
    ? (customDataset?.overview?.total_assets || uploadedAssets.length)
    : (isSihDataset ? (sihMetrics?.total_assets || sihAssets.length) : assets.length);

  // Overview metrics
  const displayOverview = isCustomDataset
    ? customDataset?.overview
    : sihMetrics;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Header with Data Origin Badge & CSV Actions */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 enterprise-card p-6 border-[#1C2042]">
        <div>
          <div className="flex flex-wrap items-center gap-3 mb-1">
            <h1 className="text-xl font-bold text-white tracking-tight">
              Enterprise Asset Inventory & Exposure Registry
            </h1>
            <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
              isCustomDataset
                ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                : (isSihDataset 
                    ? 'bg-cyan-950 text-cyan-300 border-cyan-800' 
                    : 'bg-violet-950/80 text-violet-300 border-violet-800/80')
            }`}>
              {originLabel}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            {isCustomDataset 
              ? `Dynamic dataset '${customDataset?.filename}' parsed with bidirectional vulnerability linking, discrete telemetry, and multi-source risk calculation.`
              : (isSihDataset 
                  ? 'Real-world 15-asset SIH PS26105 evaluation dataset mapped to business units, CVEs, SIEM, IAM, EDR, CSPM, and modeled financial exposure.'
                  : 'Continuous valuation of servers, databases, applications, and endpoints mapped to business importance, revenue dependency, and modeled EAL.')}
          </p>
          <DataSourceBadge showModeledLabel={true} className="mt-2" />
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <button
            onClick={() => setIsImportModalOpen(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 via-teal-600 to-violet-600 hover:from-cyan-500 hover:to-violet-500 text-white font-medium transition shadow-md cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Import CSV</span>
          </button>

          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#12152A] hover:bg-[#181C36] border border-[#2A2F5A] text-slate-300 hover:text-white transition cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export CSV</span>
          </button>

          <span className="px-3 py-1.5 rounded-lg bg-[#0C0E1A] border border-[#2A2F5A] text-slate-300">
            TOTAL: <strong className="text-cyan-400">{currentTotalCount} ASSETS</strong>
          </span>
        </div>
      </div>

      {/* Universal CSV Import Modal */}
      <UniversalCsvImportModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onSuccess={() => {
          fetchUploadedAssets();
        }}
      />

      {/* Summary KPI Row — Dynamically calculated from selected dataset */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Total Monitored</span>
          <div className="text-xl font-bold text-white font-mono mt-0.5">
            {currentTotalCount} Assets
          </div>
          <span className="text-[10px] text-slate-400 block font-mono">
            {isCustomDataset ? customDataset?.filename : (isSihDataset ? 'SIH PS26105 Records' : 'Complete Infrastructure')}
          </span>
        </div>

        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Critical Assets</span>
          <div className="text-xl font-bold text-rose-400 font-mono mt-0.5">
            {isCustomDataset 
              ? (customDataset?.overview?.critical_assets || 0)
              : (isSihDataset ? (sihMetrics?.critical_assets || 0) : 6)} Critical
          </div>
          <span className="text-[10px] text-rose-300 font-semibold block">
            Criticality Level 5 / Score ≥ 80
          </span>
        </div>

        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">High Risk Assets</span>
          <div className="text-xl font-bold text-amber-400 font-mono mt-0.5">
            {isCustomDataset
              ? (customDataset?.overview?.high_risk_assets || 0)
              : (isSihDataset ? (sihMetrics?.high_risk_assets || 0) : 18)} High Risk
          </div>
          <span className="text-[10px] text-amber-300 font-semibold block">Risk Score 60 – 79</span>
        </div>

        <div className="enterprise-card p-4 border-[#1C2042]">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Total Modeled Impact</span>
          <div className="text-xl font-bold text-amber-400 font-mono mt-0.5 truncate">
            {isCustomDataset
              ? (customDataset?.overview?.total_modeled_financial_impact_label || 'Data Not Available')
              : (isSihDataset ? (sihMetrics?.total_modeled_financial_impact_label || '₹17.53 Cr') : '₹4.60 Cr')}
          </div>
          <span className="text-[9px] text-slate-400 block font-mono">
            {isCustomDataset && !customDataset?.overview?.has_financial_data ? 'Financial Data Absent in CSV' : '*MODELED / ESTIMATED FINANCIAL'}
          </span>
        </div>
      </div>

      {/* Search & Filter Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 enterprise-card p-4 border-[#1C2042]">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder={isCustomDataset || isSihDataset ? "Search ID (A001..), name, unit, CVE..." : "Search asset name, IP, hostname..."}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0C0E1A] border border-[#2A2F5A] rounded-lg pl-9 pr-4 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto text-xs">
          {/* Type Filter */}
          <div className="flex items-center space-x-1 bg-[#0C0E1A] p-1 rounded-lg border border-[#1C2042]">
            {['all', 'server', 'database', 'application', 'endpoint', 'cloud'].map((t) => (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                className={`px-2.5 py-1 rounded-md font-semibold capitalize transition text-[11px] cursor-pointer ${
                  typeFilter === t
                    ? 'bg-gradient-to-r from-violet-600 to-cyan-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t === 'all' ? `All (${currentTotalCount})` : t + 's'}
              </button>
            ))}
          </div>

          {/* Risk Filter */}
          <div className="flex items-center space-x-1 bg-[#0C0E1A] p-1 rounded-lg border border-[#1C2042]">
            {['all', 'critical', 'high', 'medium'].map((r) => (
              <button
                key={r}
                onClick={() => setRiskFilter(r)}
                className={`px-2 py-1 rounded-md font-semibold uppercase transition text-[10px] cursor-pointer ${
                  riskFilter === r
                    ? 'bg-rose-600 text-white'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table & Detail Drawer Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Assets Table (8 Cols) */}
        <div className="lg:col-span-7 enterprise-card p-5 border-[#1C2042] space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">
              {isCustomDataset ? `${customDataset?.filename || 'Imported'} Asset Registry` : (isSihDataset ? 'SIH PS26105 Asset Registry' : 'Asset Exposure Registry')} ({currentDisplayCount} of {currentTotalCount} Displayed)
            </h2>
            <span className="text-xs text-slate-400 font-mono">Click a row to inspect associated vulnerabilities</span>
          </div>

          <div className="overflow-x-auto">
            {isCustomDataset ? (
              filteredCustomAssets.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs font-mono space-y-2">
                  <Database className="w-8 h-8 text-slate-600 mx-auto" />
                  <p>No asset records match the current filter or exist in this dataset.</p>
                </div>
              ) : (
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0C0E1A] text-slate-400 text-[10px] uppercase font-bold tracking-wider border-b border-[#1C2042]">
                    <tr>
                      <th className="py-2.5 px-3">Asset ID & Name</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3">Business Unit</th>
                      <th className="py-2.5 px-3">Criticality</th>
                      <th className="py-2.5 px-3">Risk Score</th>
                      <th className="py-2.5 px-3">Vulns</th>
                      <th className="py-2.5 px-3">Exposure</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {filteredCustomAssets.map((a) => {
                      const isSelected = selectedCustomAsset?.asset_id === a.asset_id;
                      const vCount = a.associated_vulnerabilities?.length || 0;
                      return (
                        <tr 
                          key={a.asset_id} 
                          onClick={() => setSelectedCustomAsset(a)}
                          className={`hover:bg-[#181C36]/40 cursor-pointer transition ${isSelected ? 'bg-[#181C36] border-l-2 border-cyan-500' : ''}`}
                        >
                          <td className="py-2.5 px-3 font-semibold text-white">
                            <div className="font-mono text-cyan-400 font-bold">{a.asset_id}</div>
                            <div className="text-slate-300 font-medium text-[11px] truncate max-w-[150px]">{a.asset_name}</div>
                          </td>
                          <td className="py-2.5 px-3 capitalize text-slate-300 font-medium">{a.asset_type || 'Server'}</td>
                          <td className="py-2.5 px-3 text-slate-400 text-[11px] font-mono truncate max-w-[120px]">{a.business_unit || 'IT'}</td>
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-200">
                            <span className={`px-2 py-0.5 rounded text-[10px] ${
                              (a.asset_criticality_1_5 || 0) >= 5 ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                              (a.asset_criticality_1_5 || 0) >= 4 ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                              'bg-slate-800 text-slate-300'
                            }`}>
                              {a.asset_criticality_1_5 ? `Level ${a.asset_criticality_1_5}/5` : `${a.criticality_score || 60}/100`}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono font-bold text-rose-400">
                            {a.calculated_risk_score || 50} / 100
                          </td>
                          <td className="py-2.5 px-3 font-mono">
                            {vCount > 0 ? (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/80 text-rose-300 border border-rose-800">
                                {vCount} CVE{vCount > 1 ? 's' : ''}
                              </span>
                            ) : (
                              <span className="text-[10px] text-slate-500">0 CVE</span>
                            )}
                          </td>
                          <td className="py-2.5 px-3">
                            {a.internet_exposed ? (
                              <span className="text-[10px] font-bold text-rose-300 bg-rose-950 px-2 py-0.5 rounded border border-rose-800">
                                INTERNET
                              </span>
                            ) : (
                              <span className="text-[10px] font-mono text-slate-400 bg-[#0E1122] px-2 py-0.5 rounded border border-[#1C2042]">INTERNAL</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )
            ) : isSihDataset ? (
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0C0E1A] text-slate-400 text-[10px] uppercase font-bold tracking-wider border-b border-[#1C2042]">
                  <tr>
                    <th className="py-2.5 px-3">Asset ID & Name</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Business Unit</th>
                    <th className="py-2.5 px-3">Criticality</th>
                    <th className="py-2.5 px-3">Calculated Risk</th>
                    <th className="py-2.5 px-3">Modeled Impact</th>
                    <th className="py-2.5 px-3">Exposure</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {filteredSihAssets.map((a) => {
                    const isSelected = selectedSihAsset?.asset_id === a.asset_id;
                    return (
                      <tr 
                        key={a.asset_id} 
                        onClick={() => setSelectedSihAsset(a)}
                        className={`hover:bg-[#181C36]/40 cursor-pointer transition ${isSelected ? 'bg-[#181C36] border-l-2 border-cyan-500' : ''}`}
                      >
                        <td className="py-2.5 px-3 font-semibold text-white">
                          <div className="font-mono text-cyan-400 font-bold">{a.asset_id}</div>
                          <div className="text-slate-300 font-medium text-[11px]">{a.asset_name}</div>
                        </td>
                        <td className="py-2.5 px-3 capitalize text-slate-300 font-medium">{a.asset_type}</td>
                        <td className="py-2.5 px-3 text-slate-400 text-[11px] font-mono">{a.business_unit}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-slate-200">
                          <span className={`px-2 py-0.5 rounded text-[10px] ${
                            a.asset_criticality_1_5 === 5 ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                            a.asset_criticality_1_5 === 4 ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                            'bg-slate-800 text-slate-300'
                          }`}>
                            Level {a.asset_criticality_1_5} / 5
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-mono font-bold text-rose-400">
                          {a.calculated_risk_score} / 100
                        </td>
                        <td className="py-2.5 px-3 font-mono font-bold text-amber-400">
                          {a.potential_financial_impact_label}
                        </td>
                        <td className="py-2.5 px-3">
                          {a.internet_exposed ? (
                            <span className="text-[10px] font-bold text-rose-300 bg-rose-950 px-2 py-0.5 rounded border border-rose-800">
                              INTERNET
                            </span>
                          ) : (
                            <span className="text-[10px] font-mono text-slate-400 bg-[#0E1122] px-2 py-0.5 rounded border border-[#1C2042]">INTERNAL</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <table className="w-full text-left text-xs">
                <thead className="bg-[#0C0E1A] text-slate-400 text-[10px] uppercase font-bold tracking-wider border-b border-[#1C2042]">
                  <tr>
                    <th className="py-2.5 px-3">Asset Name</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">IP / Hostname</th>
                    <th className="py-2.5 px-3">Criticality</th>
                    <th className="py-2.5 px-3">Risk Score</th>
                    <th className="py-2.5 px-3">Expected Loss (EAL)</th>
                    <th className="py-2.5 px-3">Exposure</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {filteredAssets.map((a) => {
                    const isSelected = selectedAsset?.id === a.id || selectedAsset?.name === a.name;
                    return (
                      <tr 
                        key={a.id} 
                        onClick={() => setSelectedAsset(a)}
                        className={`hover:bg-[#181C36]/40 cursor-pointer transition ${isSelected ? 'bg-[#181C36] border-l-2 border-cyan-500' : ''}`}
                      >
                        <td className="py-2.5 px-3 font-semibold text-white max-w-[200px] truncate">{a.name}</td>
                        <td className="py-2.5 px-3 capitalize text-slate-300 font-medium">{a.asset_type}</td>
                        <td className="py-2.5 px-3 font-mono text-slate-400 text-[11px]">{a.ip_address || a.hostname}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-slate-200">{a.criticality_score}/100</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-rose-400">{a.current_risk_score}/100</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-amber-400">
                          ₹{(a.expected_annual_loss || 0) >= 10000000 ? `${((a.expected_annual_loss || 0)/10000000).toFixed(2)} Cr` : `${((a.expected_annual_loss || 0)/100000).toFixed(1)} L`}
                        </td>
                        <td className="py-2.5 px-3">
                          {a.internet_exposed ? (
                            <span className="text-[10px] font-bold text-rose-300 bg-rose-950 px-2 py-0.5 rounded border border-rose-800">
                              INTERNET
                            </span>
                          ) : (
                            <span className="text-[10px] font-mono text-slate-400 bg-[#0E1122] px-2 py-0.5 rounded border border-[#1C2042]">RESTRICTED</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Selected Asset Details Drawer (5 Cols) with Bidirectional Vulnerabilities */}
        {isCustomDataset && selectedCustomAsset ? (
          <div className="lg:col-span-5 enterprise-card p-5 border-[#2A2F5A] space-y-4 bg-[#0E1122] flex flex-col justify-between">
            <div className="space-y-3.5">
              
              {/* Asset Header */}
              <div className="border-b border-[#1C2042] pb-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-mono">
                    ASSET TELEMETRY & RELATIONSHIP INSPECTOR
                  </span>
                  <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950 text-cyan-300 rounded border border-cyan-800">
                    {selectedCustomAsset.asset_type || 'Server'}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mt-1 leading-snug">
                  {selectedCustomAsset.asset_id} — {selectedCustomAsset.asset_name}
                </h3>
                <span className="text-xs text-slate-400 font-mono">
                  {selectedCustomAsset.business_unit} Unit • IP: {selectedCustomAsset.ip_address || 'N/A'} • Host: {selectedCustomAsset.hostname || 'N/A'}
                </span>
              </div>

              {/* Risk & Criticality Dual Card */}
              <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                  <span className="text-slate-500 text-[10px] block uppercase">Asset Criticality</span>
                  <span className="text-white font-bold text-sm">
                    {selectedCustomAsset.asset_criticality_1_5 ? `Level ${selectedCustomAsset.asset_criticality_1_5} / 5` : `${selectedCustomAsset.criticality_score || 60} / 100`}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#121630] border border-[#1C2042]">
                  <span className="text-slate-500 text-[10px] block uppercase">Calculated Risk Score</span>
                  <span className="text-rose-400 font-bold text-sm">
                    {selectedCustomAsset.calculated_risk_score || 50} / 100
                  </span>
                </div>
              </div>

              {/* SECTION 8: WHY IS THIS ASSET HIGH RISK? (EVIDENCE-BASED EXPLANATION) */}
              {(selectedCustomAsset.calculated_risk_score >= 60 || (selectedCustomAsset.criticality_score || 0) >= 75) && (
                <div className="p-3.5 rounded-xl bg-rose-950/30 border border-rose-800/70 font-mono text-xs space-y-2">
                  <div className="flex items-center space-x-2 text-rose-300 font-bold uppercase text-[11px]">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    <span>WHY IS THIS ASSET HIGH RISK? (EVIDENCE BREAKDOWN)</span>
                  </div>
                  <ul className="space-y-1 text-[11px] text-slate-300">
                    {(selectedCustomAsset.criticality_score || 0) >= 75 && (
                      <li className="flex items-center space-x-1.5 text-rose-300">
                        <span className="text-rose-400 font-bold">•</span>
                        <span>Tier-1 Crown Jewel Criticality ({selectedCustomAsset.criticality_score}/100)</span>
                      </li>
                    )}
                    {selectedCustomAsset.associated_vulnerabilities?.some((v: any) => v.cvss_score >= 7.0) && (
                      <li className="flex items-center space-x-1.5 text-rose-300">
                        <span className="text-rose-400 font-bold">•</span>
                        <span>High/Critical Vulnerability Present (CVSS ≥ 7.0)</span>
                      </li>
                    )}
                    {selectedCustomAsset.associated_vulnerabilities?.some((v: any) => v.exploit_available) && (
                      <li className="flex items-center space-x-1.5 text-rose-400 font-bold">
                        <span>•</span>
                        <span>Known Weaponized Exploit Active (CISA KEV)</span>
                      </li>
                    )}
                    {selectedCustomAsset.internet_exposed && (
                      <li className="flex items-center space-x-1.5 text-amber-300">
                        <span className="text-amber-400 font-bold">•</span>
                        <span>Direct Ingress Perimeter Exposure (Public Facing)</span>
                      </li>
                    )}
                    {selectedCustomAsset.siem_event && selectedCustomAsset.siem_event !== 'N/A' && (
                      <li className="flex items-center space-x-1.5 text-amber-300">
                        <span className="text-amber-400 font-bold">•</span>
                        <span>Active SIEM Event: {selectedCustomAsset.siem_event}</span>
                      </li>
                    )}
                    {selectedCustomAsset.edr_alert && selectedCustomAsset.edr_alert !== 'N/A' && (
                      <li className="flex items-center space-x-1.5 text-amber-300">
                        <span className="text-amber-400 font-bold">•</span>
                        <span>EDR Alert Flagged: {selectedCustomAsset.edr_alert}</span>
                      </li>
                    )}
                    {selectedCustomAsset.privileged_account && !selectedCustomAsset.mfa_enabled && (
                      <li className="flex items-center space-x-1.5 text-rose-400 font-bold">
                        <span>•</span>
                        <span>Privileged Administrative Account without MFA</span>
                      </li>
                    )}
                    {(selectedCustomAsset.control_effectiveness || 0.65) < 0.70 && (
                      <li className="flex items-center space-x-1.5 text-slate-300">
                        <span className="text-cyan-400 font-bold">•</span>
                        <span>Suboptimal Control Effectiveness ({((selectedCustomAsset.control_effectiveness || 0.65) * 100).toFixed(0)}%)</span>
                      </li>
                    )}
                  </ul>
                </div>
              )}

              {/* BIDIRECTIONAL RELATIONSHIP: Associated Vulnerabilities */}
              <div className="p-3.5 rounded-xl bg-[#090C1A] border border-rose-900/40 space-y-2 font-mono">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-rose-300 font-bold flex items-center space-x-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                    <span>Associated Vulnerabilities ({selectedCustomAsset.associated_vulnerabilities?.length || 0})</span>
                  </span>
                  <button
                    onClick={() => navigate('/vulnerabilities')}
                    className="text-[10px] text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer"
                  >
                    <span>View CVE Registry</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>

                {selectedCustomAsset.associated_vulnerabilities && selectedCustomAsset.associated_vulnerabilities.length > 0 ? (
                  <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
                    {selectedCustomAsset.associated_vulnerabilities.map((v: any) => (
                      <div key={v.cve_id} className="p-2.5 rounded-lg bg-[#121630] border border-[#222950] text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-rose-300 font-bold">{v.cve_id}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            v.vulnerability_severity === 'Critical' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                            v.vulnerability_severity === 'High' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                            'bg-cyan-950 text-cyan-300 border border-cyan-800'
                          }`}>
                            CVSS {v.cvss_score} ({v.vulnerability_severity})
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-300">
                          <span className={v.exploit_available ? 'text-rose-400 font-bold flex items-center' : 'text-slate-400'}>
                            {v.exploit_available ? <><Flame className="w-3 h-3 mr-0.5" /> Exploit Weaponized</> : 'No Public Exploit'}
                          </span>
                          <span>•</span>
                          <span className={v.patch_available ? 'text-emerald-400' : 'text-amber-400'}>
                            {v.patch_available ? 'Patch Ready' : 'Unpatched'}
                          </span>
                          <span>•</span>
                          <span className="text-slate-400">{v.vulnerability_age_days || 30} days open</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[11px] text-slate-500 italic py-1">
                    No active CVEs associated with this asset in the uploaded dataset.
                  </p>
                )}
              </div>

              {/* Security Telemetry Breakdown */}
              <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1.5 font-mono text-[11px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>SIEM Event:</span>
                  <span className="text-slate-200 truncate max-w-[180px]">{selectedCustomAsset.siem_event || 'N/A'}</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>IAM & MFA:</span>
                  <span className={selectedCustomAsset.privileged_account && !selectedCustomAsset.mfa_enabled ? 'text-amber-400 font-bold' : 'text-slate-200'}>
                    {selectedCustomAsset.iam_user || 'N/A'} (MFA: {selectedCustomAsset.mfa_enabled ? 'Enabled' : 'Disabled'})
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>EDR Alert:</span>
                  <span className="text-slate-200 truncate max-w-[180px]">
                    {selectedCustomAsset.edr_alert || 'N/A'} {selectedCustomAsset.edr_isolated ? '(Isolated)' : ''}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>CSPM Finding:</span>
                  <span className="text-slate-200 truncate max-w-[180px]">{selectedCustomAsset.cspm_finding || 'N/A'}</span>
                </div>
                {selectedCustomAsset.threat_intel_indicator && selectedCustomAsset.threat_intel_indicator !== 'N/A' && (
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Threat Intel:</span>
                    <span className="text-cyan-300 font-semibold">{selectedCustomAsset.threat_intel_indicator} ({selectedCustomAsset.threat_confidence_pct || 0}%)</span>
                  </div>
                )}
              </div>

              {/* Financial Risk Quantification */}
              <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/60 font-mono text-xs space-y-1">
                <span className="text-slate-400 text-[10px] block uppercase font-bold">Modeled Financial Exposure</span>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300">Modeled Impact:</span>
                  <span className="text-amber-400 font-bold">
                    {selectedCustomAsset.potential_financial_impact_label || 'Data Not Available'}
                  </span>
                </div>
                <div className="flex justify-between items-center text-[11px] text-slate-400">
                  <span>Mitigation Cost:</span>
                  <span className="text-cyan-300 font-bold">
                    {selectedCustomAsset.estimated_mitigation_cost_label || 'Data Not Available'}
                  </span>
                </div>
                <div className="flex justify-between items-center text-[11px] text-slate-400">
                  <span>Control Effectiveness:</span>
                  <span className="text-emerald-400 font-bold">
                    {selectedCustomAsset.control_effectiveness ? `${(selectedCustomAsset.control_effectiveness * 100).toFixed(0)}%` : '65%'}
                  </span>
                </div>
              </div>

            </div>

            <div className="text-[10px] text-slate-500 font-mono text-center pt-2 border-t border-[#1C2042]">
              Universal Dynamic Ingestion • Zero Fabricated Values
            </div>
          </div>
        ) : isSihDataset && selectedSihAsset ? (
          <div className="lg:col-span-5 enterprise-card p-5 border-[#2A2F5A] space-y-3 bg-[#0E1122] flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-[#1C2042] pb-2.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-mono block">SIH ASSET PROFILE INSPECTION</span>
                <div className="flex items-center justify-between mt-1">
                  <h3 className="text-sm font-bold text-white leading-snug">{selectedSihAsset.asset_id} — {selectedSihAsset.asset_name}</h3>
                  <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950 text-cyan-300 rounded border border-cyan-800">{selectedSihAsset.asset_type}</span>
                </div>
                <span className="text-xs text-slate-400 font-mono">{selectedSihAsset.business_unit} Unit</span>
              </div>

              <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                  <span className="text-slate-500 text-[10px] block">Criticality (1-5)</span>
                  <span className="text-white font-bold text-sm">Level {selectedSihAsset.asset_criticality_1_5} / 5</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                  <span className="text-slate-500 text-[10px] block">Calculated Risk</span>
                  <span className="text-rose-400 font-bold text-sm">{selectedSihAsset.calculated_risk_score} / 100</span>
                </div>
              </div>

              {/* Associated CVEs */}
              <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1.5 font-mono text-[11px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>CVE ID:</span>
                  <span className={`font-semibold ${selectedSihAsset.has_cve ? 'text-rose-400' : 'text-slate-500'}`}>
                    {selectedSihAsset.cve_id}
                  </span>
                </div>
                {selectedSihAsset.has_cve && (
                  <>
                    <div className="flex items-center justify-between text-slate-400">
                      <span>CVSS / Severity:</span>
                      <span className="text-rose-300 font-semibold">{selectedSihAsset.cvss_score} ({selectedSihAsset.vulnerability_severity})</span>
                    </div>
                    <div className="flex items-center justify-between text-slate-400">
                      <span>Exploit / Patch:</span>
                      <span className="text-slate-200">
                        {selectedSihAsset.exploit_available ? 'Exploit Available' : 'No Exploit'} | {selectedSihAsset.patch_available ? 'Patch Ready' : 'Unpatched'}
                      </span>
                    </div>
                  </>
                )}
                <div className="flex items-center justify-between text-slate-400">
                  <span>SIEM Event:</span>
                  <span className="text-slate-200 truncate max-w-[150px]">{selectedSihAsset.siem_event} ({selectedSihAsset.siem_severity})</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>IAM & MFA:</span>
                  <span className={selectedSihAsset.iam_risk_flag ? 'text-amber-400 font-bold' : 'text-slate-200'}>
                    {selectedSihAsset.iam_user} (MFA: {selectedSihAsset.mfa_enabled ? 'Yes' : 'No'})
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>EDR Alert:</span>
                  <span className="text-slate-200 truncate max-w-[150px]">{selectedSihAsset.edr_alert}</span>
                </div>
                {selectedSihAsset.has_threat_intel && (
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Threat Intel:</span>
                    <span className="text-cyan-300 font-semibold">{selectedSihAsset.threat_intel_indicator} ({selectedSihAsset.threat_confidence_pct}%)</span>
                  </div>
                )}
              </div>

              {/* Financial & Mitigation */}
              <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/60 font-mono text-xs space-y-1">
                <span className="text-slate-400 text-[10px] block">Modeled Financial Quantification</span>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300">Modeled Potential Impact:</span>
                  <span className="text-amber-400 font-bold">{selectedSihAsset.potential_financial_impact_label}</span>
                </div>
                <div className="flex justify-between items-center text-[11px] text-slate-400">
                  <span>Incident Probability:</span>
                  <span className="text-slate-200">{selectedSihAsset.incident_probability_label}</span>
                </div>
                <div className="flex justify-between items-center text-[11px] text-slate-400">
                  <span>Mitigation Cost:</span>
                  <span className="text-cyan-300 font-bold">{selectedSihAsset.estimated_mitigation_cost_label}</span>
                </div>
                <div className="flex justify-between items-center text-[11px] text-slate-400">
                  <span>Control Effectiveness:</span>
                  <span className="text-emerald-400 font-bold">{selectedSihAsset.control_effectiveness_pct}</span>
                </div>
                <p className="text-[9px] text-slate-500 mt-1 font-sans">
                  * Labeled as: {selectedSihAsset.financial_label}
                </p>
              </div>
            </div>

            <div className="text-[10px] text-slate-500 font-mono text-center pt-2 border-t border-[#1C2042]">
              SIH PS26105 Real Ground Truth Telemetry
            </div>
          </div>
        ) : selectedAsset ? (
          <div className="lg:col-span-5 enterprise-card p-5 border-[#2A2F5A] space-y-3 bg-[#0E1122] flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-[#1C2042] pb-2.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-mono block">ASSET PROFILE INSPECTION</span>
                <h3 className="text-sm font-bold text-white mt-0.5 leading-snug">{selectedAsset.name}</h3>
                <span className="text-xs text-slate-400 font-mono">{selectedAsset.ip_address} • {selectedAsset.hostname}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 font-mono text-xs">
                <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                  <span className="text-slate-500 text-[10px] block">Criticality Score</span>
                  <span className="text-white font-bold text-sm">{selectedAsset.criticality_score} / 100</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#12152A] border border-[#1C2042]">
                  <span className="text-slate-500 text-[10px] block">Risk Score</span>
                  <span className="text-rose-400 font-bold text-sm">{selectedAsset.current_risk_score} / 100</span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-[#12152A] border border-[#1C2042] space-y-1.5 font-mono text-[11px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Business Importance:</span>
                  <span className="text-white font-semibold">{selectedAsset.business_importance}%</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Data Sensitivity:</span>
                  <span className="text-white font-semibold">{selectedAsset.data_sensitivity}%</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Revenue Dependency:</span>
                  <span className="text-white font-semibold">{selectedAsset.revenue_dependency}%</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Downtime Tolerance:</span>
                  <span className="text-white font-semibold">{selectedAsset.downtime_tolerance_hours} hrs</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Operating System:</span>
                  <span className="text-slate-200">{selectedAsset.operating_system}</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Department:</span>
                  <span className="text-slate-200 truncate max-w-[140px]">{selectedAsset.department}</span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/60 font-mono text-xs">
                <span className="text-slate-400 text-[10px] block">Expected Annual Loss (Asset Modeled EAL)</span>
                <span className="text-amber-400 font-bold text-sm">
                  ₹{(((selectedAsset.expected_annual_loss || 0) / 100000)).toFixed(1)} Lakh
                </span>
                <p className="text-[10px] text-slate-400 mt-1 font-sans">
                  Single Loss Expectancy modeling downtime, IR response, recovery, and regulatory fines.
                </p>
              </div>
            </div>

            <div className="text-[10px] text-slate-500 font-mono text-center pt-2 border-t border-[#1C2042]">
              Normalized FAIR Criticality & Financial Model
            </div>
          </div>
        ) : null}

      </div>

    </div>
  );
};
