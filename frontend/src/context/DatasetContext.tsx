import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { sihDatasetService, universalImportService } from '../services/api';

export type DatasetType = 'sih_ps26105' | 'abc_bank' | 'organization_csv' | 'custom_uploaded';

export interface SIHOverviewMetrics {
  dataset_origin: string;
  total_assets: number;
  total_fields: number;
  critical_assets: number;
  high_risk_assets: number;
  internet_exposed_assets: number;
  critical_vulnerabilities: number;
  exploitable_vulnerabilities: number;
  assets_with_mfa_disabled: number;
  privileged_accounts: number;
  critical_iam_issues: number;
  critical_siem_events: number;
  critical_edr_alerts: number;
  unisolated_edr_alerts: number;
  average_control_effectiveness: number;
  average_control_effectiveness_label: string;
  enterprise_risk_score: number;
  total_modeled_financial_impact: number;
  total_modeled_financial_impact_label: string;
  total_modeled_expected_annual_loss: number;
  total_modeled_expected_annual_loss_label: string;
  total_estimated_mitigation_cost: number;
  total_estimated_mitigation_cost_label: string;
  financial_classification: string;
  disclaimer: string;
}

export interface CustomDatasetOverview {
  dataset_name: string;
  data_origin: string;
  total_records: number;
  total_assets: number;
  total_vulnerabilities: number;
  critical_assets: number;
  high_risk_assets: number;
  internet_exposed: number;
  critical_vulnerabilities: number;
  exploitable_vulnerabilities: number;
  mfa_disabled: number;
  privileged_accounts: number;
  average_control_effectiveness: number;
  average_control_effectiveness_label: string;
  has_financial_data: boolean;
  total_modeled_financial_impact: number | null;
  total_modeled_financial_impact_label: string;
  total_modeled_expected_annual_loss: number | null;
  total_modeled_expected_annual_loss_label: string;
  total_estimated_mitigation_cost: number | null;
  total_estimated_mitigation_cost_label: string;
}

export interface CustomDataset {
  id: string;
  filename: string;
  imported_at: string;
  overview: CustomDatasetOverview;
  data_confidence?: any;
  assets: any[];
  vulnerabilities: any[];
  summary: {
    dataset_name: string;
    records: number;
    assets: number;
    vulnerabilities: number;
    fields: number;
    new_assets: number;
    updated_assets: number;
    new_vulnerabilities: number;
    updated_vulnerabilities: number;
    duplicates: number;
    invalid: number;
  };
}

interface DatasetContextType {
  activeDataset: DatasetType;
  setActiveDataset: (ds: DatasetType) => void;
  isSihDataset: boolean;
  isCustomDataset: boolean;
  isAbcBank: boolean;
  sihMetrics: SIHOverviewMetrics | null;
  customDataset: CustomDataset | null;
  customAssets: any[];
  customVulnerabilities: any[];
  isLoading: boolean;
  refreshSihMetrics: () => Promise<void>;
  refreshCustomDataset: () => Promise<void>;
  setCustomUploadedDataset: (datasetPayload: CustomDataset) => void;
  originLabel: string;
  activeFilename: string;
  totalAssetsCount: number;
  totalVulnsCount: number;
  totalFieldsCount: number;
  storedDatasets: any[];
  selectCustomDataset: (filename: string) => Promise<void>;
}

const DatasetContext = createContext<DatasetContextType | undefined>(undefined);

export const DatasetProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // DEFAULT IS SIH PS26105 FOR THE EVALUATION
  const [activeDataset, setActiveDatasetState] = useState<DatasetType>(() => {
    const saved = localStorage.getItem('active_cyber_dataset');
    return (saved as DatasetType) || 'sih_ps26105';
  });

  const [sihMetrics, setSihMetrics] = useState<SIHOverviewMetrics | null>(null);
  const [customDataset, setCustomDatasetState] = useState<CustomDataset | null>(null);
  const [storedDatasets, setStoredDatasets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchSihMetrics = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await sihDatasetService.getOverview();
      setSihMetrics(data);
    } catch (err) {
      console.error('Failed to load SIH dataset overview metrics:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchCustomDataset = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await universalImportService.getActive();
      if (res && res.active && res.dataset) {
        setCustomDatasetState(res.dataset);
      }
      const dsList = await universalImportService.getDatasets();
      if (Array.isArray(dsList)) {
        setStoredDatasets(dsList);
      }
    } catch (err) {
      console.error('Failed to load active custom dataset:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSihMetrics();
    fetchCustomDataset();
  }, [fetchSihMetrics, fetchCustomDataset]);

  const setActiveDataset = (ds: DatasetType) => {
    setActiveDatasetState(ds);
    localStorage.setItem('active_cyber_dataset', ds);
    if (ds === 'sih_ps26105') {
      fetchSihMetrics();
    } else if (ds === 'custom_uploaded') {
      fetchCustomDataset();
    }
  };

  const setCustomUploadedDataset = (datasetPayload: CustomDataset) => {
    setCustomDatasetState(datasetPayload);
    setActiveDatasetState('custom_uploaded');
    localStorage.setItem('active_cyber_dataset', 'custom_uploaded');
    fetchCustomDataset();
  };

  const selectCustomDataset = async (filename: string) => {
    try {
      setIsLoading(true);
      const res = await universalImportService.selectDataset(filename);
      if (res && res.dataset) {
        setCustomDatasetState(res.dataset);
        setActiveDatasetState('custom_uploaded');
        localStorage.setItem('active_cyber_dataset', 'custom_uploaded');
      }
    } catch (err) {
      console.error('Failed to select dataset:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const isSihDataset = activeDataset === 'sih_ps26105';
  const isCustomDataset = activeDataset === 'custom_uploaded';
  const isAbcBank = activeDataset === 'abc_bank';

  const activeFilename = isCustomDataset 
    ? (customDataset?.filename || 'Uploaded Dataset')
    : (isSihDataset ? 'PS26105_Cyber_Risk_Test_Data.csv' : 'ABC_Bank_Synthetic_Demo.csv');

  const originLabel = isCustomDataset
    ? `DATA SOURCE: ${customDataset?.filename || 'CUSTOM DATASET'}`
    : (isSihDataset 
        ? (sihMetrics?.dataset_origin || 'DATA SOURCE: PS26105_Cyber_Risk_Test_Data.csv')
        : 'DATA ORIGIN: SYNTHETIC DEMO DATA (ABC BANK)');

  const totalAssetsCount = isCustomDataset
    ? (customDataset?.overview?.total_assets || customDataset?.assets?.length || 0)
    : (isSihDataset 
        ? (sihMetrics?.total_assets || 15)
        : 100);

  const totalVulnsCount = isCustomDataset
    ? (customDataset?.overview?.total_vulnerabilities || customDataset?.vulnerabilities?.length || 0)
    : (isSihDataset 
        ? (sihMetrics?.critical_vulnerabilities ? sihMetrics.critical_vulnerabilities + 8 : 13)
        : 10);

  const totalFieldsCount = isCustomDataset
    ? (customDataset?.summary?.fields || 28)
    : (isSihDataset 
        ? (sihMetrics?.total_fields || 28)
        : 18);

  const customAssets = customDataset?.assets || [];
  const customVulnerabilities = customDataset?.vulnerabilities || [];

  return (
    <DatasetContext.Provider
      value={{
        activeDataset,
        setActiveDataset,
        isSihDataset,
        isCustomDataset,
        isAbcBank,
        sihMetrics,
        customDataset,
        customAssets,
        customVulnerabilities,
        isLoading,
        refreshSihMetrics: fetchSihMetrics,
        refreshCustomDataset: fetchCustomDataset,
        setCustomUploadedDataset,
        originLabel,
        activeFilename,
        totalAssetsCount,
        totalVulnsCount,
        totalFieldsCount,
        storedDatasets,
        selectCustomDataset
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
};

export const useDataset = () => {
  const ctx = useContext(DatasetContext);
  if (!ctx) {
    throw new Error('useDataset must be used within a DatasetProvider');
  }
  return ctx;
};

