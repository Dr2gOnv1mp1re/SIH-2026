import React, { useState } from 'react';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  X,
  ArrowRight,
  ArrowLeft,
  Database,
  ShieldAlert,
  Layers,
  Cpu,
  DollarSign,
  Table,
  Check,
  Eye,
  FileText,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { universalImportService, assetService } from '../services/api';
import { useDataset, CustomDataset } from '../context/DatasetContext';

const CANONICAL_TARGET_FIELDS = [
  {
    group: 'Asset Inventory', fields: [
      { key: 'asset_id', label: 'Asset ID (Unique Identifier)', module: 'Asset Inventory' },
      { key: 'asset_name', label: 'Asset Name / Server Name', module: 'Asset Inventory' },
      { key: 'asset_type', label: 'Asset Type (Server, DB, App, Cloud)', module: 'Asset Inventory' },
      { key: 'ip_address', label: 'IP Address', module: 'Asset Inventory' },
      { key: 'hostname', label: 'Hostname / FQDN', module: 'Asset Inventory' },
      { key: 'asset_criticality', label: 'Asset Criticality (1-5 or 0-100)', module: 'Asset Inventory' },
      { key: 'business_unit', label: 'Business Unit / Department', module: 'Asset Inventory' },
      { key: 'internet_exposed', label: 'Internet Exposed (Yes/No)', module: 'Asset Inventory' }
    ]
  },
  {
    group: 'Vulnerabilities', fields: [
      { key: 'cve_id', label: 'CVE Identifier (CVE-YYYY-NNNN)', module: 'Vulnerabilities' },
      { key: 'cvss_score', label: 'CVSS Base Score (0.0 - 10.0)', module: 'Vulnerabilities' },
      { key: 'vulnerability_severity', label: 'Severity (Critical, High, Med, Low)', module: 'Vulnerabilities' },
      { key: 'exploit_available', label: 'Exploit Weaponized / Available', module: 'Vulnerabilities' },
      { key: 'patch_available', label: 'Patch Available / Ready', module: 'Vulnerabilities' },
      { key: 'vulnerability_age_days', label: 'Vulnerability Age (Days)', module: 'Vulnerabilities' },
      { key: 'vulnerability_description', label: 'Description / CVE Title', module: 'Vulnerabilities' }
    ]
  },
  {
    group: 'Security Telemetry (SIEM, IAM, EDR, CSPM)', fields: [
      { key: 'siem_event', label: 'SIEM Security Event', module: 'SIEM / Events' },
      { key: 'siem_severity', label: 'SIEM Event Severity', module: 'SIEM / Events' },
      { key: 'iam_user', label: 'IAM User / Identity', module: 'IAM & Access' },
      { key: 'mfa_enabled', label: 'MFA Status (Enabled/Disabled)', module: 'IAM & Access' },
      { key: 'privileged_account', label: 'Privileged Account (Admin/Root)', module: 'IAM & Access' },
      { key: 'edr_alert', label: 'EDR Alert / Detection', module: 'EDR Telemetry' },
      { key: 'edr_severity', label: 'EDR Alert Severity', module: 'EDR Telemetry' },
      { key: 'edr_isolated', label: 'EDR Network Isolated', module: 'EDR Telemetry' },
      { key: 'cspm_finding', label: 'CSPM Cloud Finding', module: 'CSPM Cloud' },
      { key: 'cspm_severity', label: 'CSPM Finding Severity', module: 'CSPM Cloud' }
    ]
  },
  {
    group: 'Threat Intelligence', fields: [
      { key: 'threat_intel_indicator', label: 'Threat Intel Indicator / Campaign', module: 'Threat Intel' },
      { key: 'threat_confidence_pct', label: 'Threat Confidence (%)', module: 'Threat Intel' }
    ]
  },
  {
    group: 'Financial & Security Controls', fields: [
      { key: 'estimated_incident_probability', label: 'Incident Probability (0.0 - 1.0)', module: 'Financial Risk' },
      { key: 'potential_financial_impact_inr', label: 'Potential Financial Impact (INR)', module: 'Financial Risk' },
      { key: 'estimated_mitigation_cost_inr', label: 'Mitigation Cost (INR)', module: 'Security Controls' },
      { key: 'control_effectiveness', label: 'Control Effectiveness (0.0 - 1.0)', module: 'Security Controls' }
    ]
  },
  {
    group: 'Ignore / Skip', fields: [
      { key: 'unmapped', label: '— Unmapped / Ignore Column —', module: 'Ignore' }
    ]
  }
];

interface UniversalCsvImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (dataset: CustomDataset) => void;
}

export const UniversalCsvImportModal: React.FC<UniversalCsvImportModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const navigate = useNavigate();
  const { setCustomUploadedDataset } = useDataset();

  // Wizard state: 1: upload/input, 2: mapping & preview, 3: success summary
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [rawCsvText, setRawCsvText] = useState<string>('');
  const [filename, setFilename] = useState<string>('cyber_risk_dataset.csv');

  // Analysis state from backend detection
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [userMappings, setUserMappings] = useState<Record<string, string>>({});
  const [duplicateStrategy, setDuplicateStrategy] = useState<'update_existing' | 'add_new' | 'skip_duplicates'>('update_existing');

  // Loading & error handling
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [importedSummary, setImportedSummary] = useState<any | null>(null);

  if (!isOpen) return null;

  const handleFileSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setFilename(file.name);
    setErrorMessage(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setRawCsvText(text);
    };
    reader.readAsText(file);
  };

  const handleLoadSampleSih = () => {
    const sample = `asset_id,asset_name,asset_type,business_unit,asset_criticality_1_5,internet_exposed,cve_id,cvss_score,vulnerability_severity,patch_available,exploit_available,vulnerability_age_days,siem_event,siem_severity,iam_user,mfa_enabled,privileged_account,edr_alert,edr_severity,edr_isolated,cspm_finding,cspm_severity,threat_intel_indicator,threat_confidence_pct,estimated_incident_probability,potential_financial_impact_inr,estimated_mitigation_cost_inr,control_effectiveness
A001,ERP-APP-01,Application Server,Finance,5,Yes,CVE-2026-1001,9.8,Critical,Yes,Yes,120,Multiple Failed Admin Logins,High,admin_fin01,No,Yes,Suspicious PowerShell,High,No,N/A,N/A,Known Exploited Vulnerability,95,0.28,12000000,250000,0.78
A002,ERP-DB-01,Database,Finance,5,No,CVE-2026-1002,8.8,High,Yes,Yes,75,Unusual Database Query Volume,Medium,dbadmin01,Yes,Yes,No Active Alert,Low,Yes,N/A,N/A,Exploit Available,82,0.16,15000000,180000,0.86
A003,HR-PORTAL-01,Web Server,HR,4,Yes,CVE-2026-1003,9.1,Critical,Yes,Yes,190,Web Attack Detected,High,hradmin,No,Yes,Web Shell Behavior,Critical,No,N/A,N/A,Active Exploitation Campaign,93,0.34,7000000,220000,0.64
A004,CRM-APP-01,Application Server,Sales,4,Yes,CVE-2026-1004,7.5,High,Yes,No,45,Repeated Login Failures,Medium,crmadmin,Yes,Yes,No Active Alert,Low,Yes,N/A,N/A,No Known Exploitation,40,0.09,5000000,150000,0.82
A005,PAYMENT-GW-01,Payment Gateway,Finance,5,Yes,CVE-2026-1005,9.9,Critical,Yes,Yes,30,Credential Stuffing,Critical,payadmin,No,Yes,Credential Dumping Attempt,Critical,No,N/A,N/A,Ransomware Group Targeting Sector,97,0.42,25000000,600000,0.58
A006,EMP-LAP-021,Endpoint,Engineering,2,No,CVE-2026-1006,6.5,Medium,Yes,No,210,Malicious Attachment Opened,High,employee021,Yes,No,Malware Detected,High,Yes,N/A,N/A,Commodity Malware,67,0.08,800000,30000,0.88
A007,DC-01,Domain Controller,IT,5,No,CVE-2026-1007,8.1,High,Yes,Yes,95,Privileged Group Modification,Critical,domainadmin02,No,Yes,LSASS Access Attempt,Critical,No,N/A,N/A,Credential Theft TTP,91,0.31,18000000,400000,0.61
A008,FILE-SRV-01,File Server,Operations,4,No,CVE-2026-1008,7.8,High,Yes,Yes,160,Large File Encryption Activity,Critical,opsadmin,Yes,Yes,Ransomware Behavior,Critical,No,N/A,N/A,Ransomware Indicator,96,0.37,9000000,350000,0.55
A009,AWS-S3-CUSTDATA,Cloud Storage,Customer Services,5,Yes,N/A,0.0,N/A,N/A,N/A,0,Public Access Policy Change,High,cloudadmin,Yes,Yes,N/A,N/A,N/A,Public Bucket,Critical,Cloud Data Exposure Campaign,88,0.26,20000000,200000,0.69
A010,AWS-IAM-ROOT,Cloud Identity,IT,5,Yes,N/A,0.0,N/A,N/A,N/A,0,Root Login Without MFA,Critical,root,No,Yes,N/A,N/A,N/A,Root Account MFA Disabled,Critical,Cloud Account Takeover Activity,94,0.39,22000000,100000,0.52
A011,VPN-GW-01,VPN Gateway,IT,5,Yes,CVE-2026-1011,9.4,Critical,Yes,Yes,110,Multiple Foreign Login Attempts,High,vpnadmin,No,Yes,N/A,N/A,N/A,N/A,N/A,VPN Appliance Exploitation,92,0.36,16000000,300000,0.6
A012,MAIL-SRV-01,Mail Server,Corporate,4,Yes,CVE-2026-1012,8.5,High,Yes,Yes,65,Suspicious Mailbox Rule,High,mailadmin,Yes,Yes,Malicious Process Spawned,High,No,N/A,N/A,Phishing Infrastructure Detected,84,0.21,6500000,180000,0.72
A013,BACKUP-SRV-01,Backup Server,IT,5,No,CVE-2026-1013,7.2,High,Yes,No,250,Backup Deletion Attempt,Critical,backupadmin,No,Yes,Privilege Escalation,High,No,N/A,N/A,Ransomware Precursor Activity,90,0.29,14000000,275000,0.63
A014,DEV-GIT-01,Source Code Repository,Engineering,4,Yes,CVE-2026-1014,6.8,Medium,Yes,No,85,Token Used From New Geography,Medium,devadmin,Yes,Yes,N/A,N/A,N/A,N/A,N/A,Developer Credential Theft,74,0.12,4000000,120000,0.8
A015,IOT-CAM-01,IoT Device,Facilities,2,Yes,CVE-2026-1015,9.0,Critical,No,Yes,400,Outbound Connection To Unknown IP,High,iotadmin,No,Yes,N/A,N/A,N/A,Default Credentials,High,Botnet Infrastructure,89,0.24,1000000,45000,0.47`;
    setRawCsvText(sample);
    setFilename('PS26105_Cyber_Risk_Test_Data.csv');
    setSelectedFile(null);
    setErrorMessage(null);
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
    } catch (e) {
      alert('Failed to download template.');
    }
  };

  // Analyze CSV or ZIP package
  const handleAnalyzeCSV = async () => {
    if (!selectedFile && !rawCsvText.trim()) {
      setErrorMessage('Please choose a CSV/ZIP file or paste valid CSV content.');
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      let analysis;
      if (selectedFile) {
        if (selectedFile.name.toLowerCase().endsWith('.zip')) {
          analysis = await universalImportService.detectPackage(selectedFile);
        } else {
          analysis = await universalImportService.detectMappings(selectedFile);
        }
      } else {
        analysis = await universalImportService.analyzeRaw(rawCsvText, filename);
      }

      setAnalysisResult(analysis);
      // Initialize user mappings with auto-detected ones if single CSV
      const initialMap: Record<string, string> = {};
      if (analysis && analysis.mappings) {
        analysis.mappings.forEach((m: any) => {
          initialMap[m.csv_column] = m.target_field;
        });
      }
      setUserMappings(initialMap);
      setStep(2);
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to analyze file.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleMappingChange = (csvCol: string, targetKey: string) => {
    setUserMappings(prev => ({
      ...prev,
      [csvCol]: targetKey
    }));
  };

  // Execute Import
  const handleExecuteImport = async () => {
    setIsProcessing(true);
    setErrorMessage(null);

    try {
      let res;
      if (selectedFile && selectedFile.name.toLowerCase().endsWith('.zip')) {
        res = await universalImportService.executePackage(selectedFile, duplicateStrategy);
      } else {
        res = await universalImportService.executeImport({
          file: selectedFile || undefined,
          csv_content: rawCsvText || undefined,
          filename: filename,
          custom_mappings: userMappings,
          duplicate_strategy: duplicateStrategy
        });
      }

      if (res && res.dataset) {
        setImportedSummary(res.dataset.summary);
        setCustomUploadedDataset(res.dataset);
        if (onSuccess) {
          onSuccess(res.dataset);
        }
        setStep(3);
      } else {
        throw new Error('Import response was incomplete.');
      }
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || err.message || 'Failed to complete import.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-[#0b0e20] border border-cyan-500/50 rounded-2xl max-w-4xl w-full p-6 shadow-2xl relative my-8 text-slate-200 animate-in fade-in zoom-in-95 duration-200">

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#181D3C] transition cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3 mb-4 border-b border-[#1C2242] pb-4">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-900/60 to-violet-900/60 border border-cyan-500/40 text-cyan-300 shadow-md">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-white tracking-tight">
                Universal Cybersecurity CSV Import & Analysis
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-800">
                MULTI-FORMAT ENGINE
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Upload any compatible cybersecurity dataset (Assets, CVEs, SIEM, IAM, EDR, CSPM, Threat Intel, Financials).
            </p>
          </div>
        </div>

        {/* Step Indicator */}
        <div className="grid grid-cols-3 gap-2 mb-5 text-xs font-mono">
          <div className={`p-2.5 rounded-lg border flex items-center space-x-2 transition ${step === 1 ? 'bg-cyan-950/70 border-cyan-500 text-cyan-300 font-bold' : 'bg-[#10142B] border-[#1C2242] text-slate-400'
            }`}>
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${step === 1 ? 'bg-cyan-500 text-black' : (step > 1 ? 'bg-emerald-500 text-black' : 'bg-slate-700 text-white')
              }`}>
              {step > 1 ? <Check className="w-3 h-3" /> : '1'}
            </span>
            <span>1. Upload Dataset</span>
          </div>

          <div className={`p-2.5 rounded-lg border flex items-center space-x-2 transition ${step === 2 ? 'bg-cyan-950/70 border-cyan-500 text-cyan-300 font-bold' : 'bg-[#10142B] border-[#1C2242] text-slate-400'
            }`}>
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${step === 2 ? 'bg-cyan-500 text-black' : (step > 2 ? 'bg-emerald-500 text-black' : 'bg-slate-700 text-white')
              }`}>
              {step > 2 ? <Check className="w-3 h-3" /> : '2'}
            </span>
            <span>2. Map & Validate</span>
          </div>

          <div className={`p-2.5 rounded-lg border flex items-center space-x-2 transition ${step === 3 ? 'bg-emerald-950/70 border-emerald-500 text-emerald-300 font-bold' : 'bg-[#10142B] border-[#1C2242] text-slate-400'
            }`}>
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${step === 3 ? 'bg-emerald-500 text-black' : 'bg-slate-700 text-white'
              }`}>
              3
            </span>
            <span>3. Summary & Launch</span>
          </div>
        </div>

        {/* Error Alert Box */}
        {errorMessage && (
          <div className="p-3 mb-4 rounded-xl bg-rose-950/50 border border-rose-600/60 text-rose-300 text-xs flex items-center space-x-2 font-mono">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* ========================================================================= */}
        {/* STEP 1: Upload & Format Selection                                         */}
        {/* ========================================================================= */}
        {step === 1 && (
          <div className="space-y-4">

            {/* Quick Actions Bar */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-[#121630] border border-[#1C2242] text-xs">
              <div className="flex items-center space-x-2 text-slate-300">
                <HelpCircle className="w-4 h-4 text-cyan-400" />
                <span>Compatible with Asset-only, Vuln-only, Asset+CVE, and Telemetry CSVs.</span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleLoadSampleSih}
                  className="px-2.5 py-1 rounded-md bg-cyan-950 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 font-mono font-semibold transition"
                >
                  Load SIH PS26105 Test Data
                </button>
                <button
                  onClick={handleDownloadTemplate}
                  className="px-2.5 py-1 rounded-md bg-[#181E3E] hover:bg-[#202750] border border-[#2B3566] text-slate-300 hover:text-white font-mono transition"
                >
                  Download Template
                </button>
              </div>
            </div>

            {/* File Dropzone */}
            <div className="border-2 border-dashed border-[#293266] hover:border-cyan-500/70 rounded-2xl p-6 text-center transition bg-[#090C1B]/60">
              <input
                type="file"
                accept=".zip,.csv,text/csv,application/zip,application/x-zip-compressed"
                id="universal-csv-input"
                onChange={handleFileSelected}
                className="hidden"
              />
              <label htmlFor="universal-csv-input" className="cursor-pointer flex flex-col items-center">
                <div className="p-3 rounded-full bg-cyan-950/60 border border-cyan-700/50 text-cyan-400 mb-2">
                  <Upload className="w-6 h-6" />
                </div>
                <span className="text-sm font-semibold text-white">
                  {selectedFile ? selectedFile.name : 'Select or Drop Sir Data Package (.ZIP) or CSV'}
                </span>
                <span className="text-xs text-slate-400 mt-1">
                  Supports ZIP Packages with multiple CSV/JSON files or single CSV files
                </span>
              </label>
            </div>

            {/* Raw Text Fallback */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold text-slate-400 uppercase font-mono">
                  Or Paste Raw CSV Content Below
                </label>
                <span className="text-[10px] text-slate-500 font-mono">
                  {rawCsvText.length > 0 ? `${rawCsvText.split('\n').length} lines detected` : ''}
                </span>
              </div>
              <textarea
                rows={6}
                value={rawCsvText}
                onChange={(e) => setRawCsvText(e.target.value)}
                placeholder="asset_id,asset_name,cve_id,cvss_score,vulnerability_severity,patch_available,exploit_available..."
                className="w-full bg-[#080A16] border border-[#222950] rounded-xl p-3 text-xs text-cyan-200 font-mono focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-2 border-t border-[#1C2242]">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleAnalyzeCSV}
                disabled={isProcessing || (!selectedFile && !rawCsvText.trim())}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-violet-600 hover:from-cyan-500 hover:to-violet-500 disabled:opacity-50 text-xs font-bold text-white transition flex items-center space-x-2 shadow-lg shadow-cyan-900/30 cursor-pointer"
              >
                {isProcessing ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Analyzing Package / CSV...</span>
                  </>
                ) : (
                  <>
                    <span>Inspect & Map Package</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

          </div>
        )}

        {/* ========================================================================= */}
        {/* STEP 2: Interactive Mapping & Validation Preview                          */}
        {/* ========================================================================= */}
        {step === 2 && analysisResult && (
          <div className="space-y-4">

            {/* If ZIP PACKAGE: Render Multi-File Package Preview */}
            {analysisResult.is_package ? (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-950/70 via-[#10142C] to-violet-950/70 border border-cyan-500/40">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-widest text-cyan-400 font-bold">
                        SIR DATA PACKAGE DETECTED
                      </span>
                      <h3 className="text-base font-bold text-white font-mono mt-0.5">
                        {analysisResult.package_name || 'data_package.zip'}
                      </h3>
                    </div>
                    <div className="text-right font-mono">
                      <span className="text-xs text-slate-400 block">Total Package Records</span>
                      <span className="text-lg font-bold text-cyan-300">{analysisResult.total_records} Records</span>
                    </div>
                  </div>
                </div>

                {/* Package Files Table */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <span className="flex items-center space-x-1.5">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      <span>DETECTED FILES ({analysisResult.files?.length || 0} Files)</span>
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      Auto-classified based on content & schemas
                    </span>
                  </div>

                  <div className="max-h-60 overflow-y-auto rounded-xl border border-[#1C2242] bg-[#070914]">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#0e1124] text-slate-400 text-[10px] uppercase font-bold sticky top-0 border-b border-[#1C2242]">
                        <tr>
                          <th className="py-2.5 px-3">Filename</th>
                          <th className="py-2.5 px-3">Record Count</th>
                          <th className="py-2.5 px-3">Detected Data Type</th>
                          <th className="py-2.5 px-3">Mapped Module</th>
                          <th className="py-2.5 px-3">Import Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50 font-mono text-xs">
                        {analysisResult.files?.map((f: any) => (
                          <tr key={f.filename} className="hover:bg-[#121630]/60 transition">
                            <td className="py-2.5 px-3 font-bold text-cyan-300 flex items-center space-x-2">
                              <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                              <span>{f.filename}</span>
                            </td>
                            <td className="py-2.5 px-3 text-white font-semibold">
                              {f.record_count} Records
                            </td>
                            <td className="py-2.5 px-3">
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-violet-950 text-violet-300 border border-violet-800">
                                {f.detected_data_type}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-slate-300 font-sans font-medium">
                              {f.mapped_module}
                            </td>
                            <td className="py-2.5 px-3">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${f.status === 'READY'
                                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                                : 'bg-rose-950 text-rose-300 border border-rose-800'
                                }`}>
                                {f.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Duplicate Strategy Row */}
                <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-[#10142C] border border-[#1D244A] text-xs">
                  <span className="text-slate-300 font-semibold flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span>Duplicate Handling Strategy:</span>
                  </span>
                  <div className="flex items-center space-x-2 font-mono text-[11px]">
                    {[
                      { key: 'update_existing', label: 'UPDATE EXISTING' },
                      { key: 'add_new', label: 'ADD NEW' },
                      { key: 'skip_duplicates', label: 'SKIP DUPLICATES' }
                    ].map((strat) => (
                      <button
                        key={strat.key}
                        type="button"
                        onClick={() => setDuplicateStrategy(strat.key as any)}
                        className={`px-2.5 py-1 rounded-md font-semibold transition cursor-pointer ${duplicateStrategy === strat.key
                          ? 'bg-cyan-500 text-black shadow'
                          : 'bg-[#181D3C] text-slate-400 hover:text-white border border-[#2B3566]'
                          }`}
                      >
                        {strat.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Modal Actions */}
                <div className="flex items-center justify-between pt-2 border-t border-[#1C2242]">
                  <button
                    onClick={() => setStep(1)}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition flex items-center space-x-1.5 cursor-pointer"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Back to Upload</span>
                  </button>

                  <button
                    onClick={handleExecuteImport}
                    disabled={isProcessing}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-cyan-600 to-violet-600 hover:from-emerald-500 hover:to-violet-500 disabled:opacity-50 text-xs font-bold text-white transition flex items-center space-x-2 shadow-lg shadow-cyan-900/30 cursor-pointer"
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Importing All Files & Correlating Records...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Import All</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              /* Single CSV Mapping View */
              <div className="space-y-4">
                {/* Format & Statistics Badge Row */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-[#121630] border border-[#222B57]">
                    <span className="text-[10px] text-slate-400 block uppercase">CSV File</span>
                    <span className="text-xs font-bold text-cyan-300 truncate block mt-0.5">
                      {analysisResult.filename || filename}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-[#121630] border border-[#222B57]">
                    <span className="text-[10px] text-slate-400 block uppercase">Total Records</span>
                    <span className="text-base font-bold text-white mt-0.5">
                      {analysisResult.total_rows}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-[#121630] border border-[#222B57]">
                    <span className="text-[10px] text-slate-400 block uppercase">Detected Assets</span>
                    <span className="text-base font-bold text-emerald-400 mt-0.5">
                      {analysisResult.detected_unique_assets} Assets
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-[#121630] border border-[#222B57]">
                    <span className="text-[10px] text-slate-400 block uppercase">Detected CVEs</span>
                    <span className="text-base font-bold text-rose-400 mt-0.5">
                      {analysisResult.detected_unique_cves} CVEs
                    </span>
                  </div>
                </div>

                {/* Detected Data Categories Breakdown */}
                {analysisResult.detected_categories && analysisResult.detected_categories.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-[#0e122b] border border-cyan-800/40 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-mono font-bold uppercase text-cyan-400 flex items-center space-x-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>DETECTED DATA IN CSV:</span>
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        Normalized across {analysisResult.total_headers_count || 28} fields
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.detected_categories.map((cat: string) => (
                        <span
                          key={cat}
                          className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-emerald-950/80 border border-emerald-600/60 text-emerald-300 flex items-center space-x-1.5 shadow-sm"
                        >
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span>{cat}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Validation Warnings if any */}
                {analysisResult.validation_warnings && analysisResult.validation_warnings.length > 0 && (
                  <div className="p-3 rounded-xl bg-amber-950/40 border border-amber-600/50 text-amber-300 text-xs space-y-1 font-mono">
                    <div className="flex items-center space-x-1 font-bold text-[11px]">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                      <span>Validation Notices ({analysisResult.validation_warnings.length}):</span>
                    </div>
                    <ul className="list-disc list-inside text-[10px] text-slate-300 space-y-0.5">
                      {analysisResult.validation_warnings.slice(0, 3).map((w: string, idx: number) => (
                        <li key={idx}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Duplicate Strategy Row */}
                <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-[#10142C] border border-[#1D244A] text-xs">
                  <span className="text-slate-300 font-semibold flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span>Duplicate Handling Strategy:</span>
                  </span>
                  <div className="flex items-center space-x-2 font-mono text-[11px]">
                    {[
                      { key: 'update_existing', label: 'UPDATE EXISTING' },
                      { key: 'add_new', label: 'ADD NEW' },
                      { key: 'skip_duplicates', label: 'SKIP DUPLICATES' }
                    ].map((strat) => (
                      <button
                        key={strat.key}
                        type="button"
                        onClick={() => setDuplicateStrategy(strat.key as any)}
                        className={`px-2.5 py-1 rounded-md font-semibold transition cursor-pointer ${duplicateStrategy === strat.key
                          ? 'bg-cyan-500 text-black shadow'
                          : 'bg-[#181D3C] text-slate-400 hover:text-white border border-[#2B3566]'
                          }`}
                      >
                        {strat.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Interactive Mapping Table */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                    <span className="flex items-center space-x-1.5">
                      <Table className="w-4 h-4 text-cyan-400" />
                      <span>CSV FIELD MAPPING ({analysisResult.mappings?.length || 0} Columns)</span>
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      Review or adjust detected mappings before importing
                    </span>
                  </div>

                  <div className="max-h-60 overflow-y-auto rounded-xl border border-[#1C2242] bg-[#070914]">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#0e1124] text-slate-400 text-[10px] uppercase font-bold sticky top-0 border-b border-[#1C2242]">
                        <tr>
                          <th className="py-2.5 px-3">CSV Column</th>
                          <th className="py-2.5 px-3">Detected Meaning</th>
                          <th className="py-2.5 px-3">Application Target Field</th>
                          <th className="py-2.5 px-3">Module</th>
                          <th className="py-2.5 px-3">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/50 font-sans">
                        {analysisResult.mappings?.map((m: any) => {
                          const currentSelected = userMappings[m.csv_column] || m.target_field;
                          const isMapped = currentSelected !== 'unmapped';

                          return (
                            <tr key={m.csv_column} className="hover:bg-[#121630]/60 transition">
                              <td className="py-2 px-3 font-mono font-bold text-cyan-300">
                                {m.csv_column}
                              </td>
                              <td className="py-2 px-3 text-slate-300 font-medium">
                                {m.detected_meaning}
                              </td>
                              <td className="py-2 px-3">
                                <select
                                  value={currentSelected}
                                  onChange={(e) => handleMappingChange(m.csv_column, e.target.value)}
                                  className="bg-[#10142C] border border-cyan-500/30 text-white rounded-lg px-2.5 py-1 text-xs font-mono focus:outline-none focus:border-cyan-400 cursor-pointer w-full max-w-[220px]"
                                >
                                  {CANONICAL_TARGET_FIELDS.map((group) => (
                                    <optgroup key={group.group} label={group.group}>
                                      {group.fields.map((f) => (
                                        <option key={f.key} value={f.key}>
                                          {f.label}
                                        </option>
                                      ))}
                                    </optgroup>
                                  ))}
                                </select>
                              </td>
                              <td className="py-2 px-3 font-mono text-[11px] text-slate-400">
                                {m.module}
                              </td>
                              <td className="py-2 px-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${isMapped
                                  ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                                  : 'bg-amber-950/80 text-amber-300 border border-amber-800'
                                  }`}>
                                  {isMapped ? 'Mapped' : 'Unmapped'}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Live Data Preview of 5 Rows */}
                {analysisResult.preview_rows && analysisResult.preview_rows.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-bold text-slate-400 uppercase font-mono block">
                      Sample Parsed Records (First {analysisResult.preview_rows.length} rows)
                    </span>
                    <div className="max-h-32 overflow-x-auto overflow-y-auto rounded-xl border border-[#1C2242] bg-[#070914] text-[11px] font-mono p-2">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="text-slate-500 border-b border-slate-800 text-[10px]">
                            {Object.keys(analysisResult.preview_rows[0]).map((col) => (
                              <th key={col} className="p-1 px-2 whitespace-nowrap">{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-900 text-slate-300">
                          {analysisResult.preview_rows.map((row: any, rIdx: number) => (
                            <tr key={rIdx} className="hover:bg-slate-900/50">
                              {Object.values(row).map((val: any, cIdx: number) => (
                                <td key={cIdx} className="p-1 px-2 whitespace-nowrap">{String(val)}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Modal Actions */}
                <div className="flex items-center justify-between pt-2 border-t border-[#1C2242]">
                  <button
                    onClick={() => setStep(1)}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition flex items-center space-x-1.5 cursor-pointer"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Back to Upload</span>
                  </button>

                  <button
                    onClick={handleExecuteImport}
                    disabled={isProcessing}
                    className="px-6 py-2 rounded-xl bg-gradient-to-r from-emerald-600 via-cyan-600 to-violet-600 hover:from-emerald-500 hover:to-violet-500 disabled:opacity-50 text-xs font-bold text-white transition flex items-center space-x-2 shadow-lg shadow-cyan-900/30 cursor-pointer"
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Ingesting & Recalculating Risk...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Import & Analyze</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

          </div>
        )}

        {/* ========================================================================= */}
        {/* STEP 3: Import Summary & Immediate Navigation                             */}
        {/* ========================================================================= */}
        {step === 3 && importedSummary && (
          <div className="space-y-5 py-2">

            <div className="text-center space-y-2">
              <div className="inline-flex p-3 rounded-2xl bg-emerald-950/80 border border-emerald-500 text-emerald-300 shadow-xl shadow-emerald-950/50">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-extrabold text-white tracking-tight">
                IMPORT COMPLETE
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Dataset <strong className="text-cyan-300">&apos;{importedSummary.dataset_name}&apos;</strong> has been integrated into the database and modules.
              </p>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
              <div className="p-3.5 rounded-xl bg-[#121630] border border-cyan-800/50 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Total Records</span>
                <span className="text-xl font-bold text-white mt-1 block">{importedSummary.records}</span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#121630] border border-emerald-800/50 text-center">
                <span className="text-[10px] text-emerald-400 uppercase font-semibold block">Assets Imported</span>
                <span className="text-xl font-bold text-emerald-300 mt-1 block">{importedSummary.assets}</span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#121630] border border-rose-800/50 text-center">
                <span className="text-[10px] text-rose-400 uppercase font-semibold block">Vulnerabilities</span>
                <span className="text-xl font-bold text-rose-300 mt-1 block">{importedSummary.vulnerabilities}</span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#121630] border border-violet-800/50 text-center">
                <span className="text-[10px] text-violet-400 uppercase font-semibold block">Files Processed</span>
                <span className="text-xl font-bold text-violet-300 mt-1 block">{importedSummary.files_processed || 1}</span>
              </div>
            </div>

            {/* Sub-module Breakdown Table */}
            <div className="p-4 rounded-xl bg-[#0B0E20] border border-[#1C2242] text-xs font-mono grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-2 rounded-lg bg-[#111633] border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">SIEM Records:</span>
                <span className="text-cyan-300 font-bold">{importedSummary.siem_records ?? 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-[#111633] border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">IAM Records:</span>
                <span className="text-cyan-300 font-bold">{importedSummary.iam_records ?? 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-[#111633] border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">EDR Records:</span>
                <span className="text-cyan-300 font-bold">{importedSummary.edr_records ?? 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-[#111633] border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">CSPM Records:</span>
                <span className="text-cyan-300 font-bold">{importedSummary.cspm_records ?? 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-[#111633] border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">Threat Records:</span>
                <span className="text-cyan-300 font-bold">{importedSummary.threat_records ?? 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-[#111633] border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">Financial Records:</span>
                <span className="text-cyan-300 font-bold">{importedSummary.financial_records ?? 0}</span>
              </div>
            </div>

            {/* Final Action Navigation Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              <button
                onClick={() => {
                  onClose();
                  navigate('/assets');
                }}
                className="p-3 rounded-xl bg-[#161C3C] hover:bg-[#202752] border border-cyan-500/40 text-cyan-300 hover:text-white text-xs font-bold font-mono transition flex items-center justify-center space-x-2 cursor-pointer shadow-md"
              >
                <Database className="w-4 h-4" />
                <span>VIEW ASSETS</span>
              </button>

              <button
                onClick={() => {
                  onClose();
                  navigate('/vulnerabilities');
                }}
                className="p-3 rounded-xl bg-[#161C3C] hover:bg-[#202752] border border-rose-500/40 text-rose-300 hover:text-white text-xs font-bold font-mono transition flex items-center justify-center space-x-2 cursor-pointer shadow-md"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>VIEW VULNERABILITIES</span>
              </button>

              <button
                onClick={() => {
                  onClose();
                  navigate('/ciso');
                }}
                className="p-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white text-xs font-bold font-mono transition flex items-center justify-center space-x-2 cursor-pointer shadow-lg shadow-cyan-950/50"
              >
                <Cpu className="w-4 h-4" />
                <span>VIEW IMPORTED DATA</span>
              </button>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};
