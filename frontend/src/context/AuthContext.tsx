import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, Organization } from '../types';
import { authService, organizationService } from '../services/api';

interface AuthContextType {
  user: User | null;
  organization: Organization | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password?: string) => Promise<void>;
  logout: () => void;
  switchRole: (role: 'CISO' | 'SECURITY_ANALYST' | 'RISK_ANALYST' | 'EXECUTIVE' | 'AUDITOR' | 'ADMIN', customPassword?: string) => Promise<void>;
  updateUserPassword: (role: string, newPassword: string) => void;
  getRolePassword: (role: string) => string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const ROLE_PRESETS = {
  ADMIN: { id: 'usr-admin-01', email: 'admin@abcbank.com', full_name: 'Admin User', role: 'ADMIN' as const },
  CISO: { id: 'usr-ciso-01', email: 'ciso@abcbank.com', full_name: 'Vikram Malhotra (CISO)', role: 'CISO' as const },
  SECURITY_ANALYST: { id: 'usr-analyst-01', email: 'analyst@abcbank.com', full_name: 'Priya Sharma (Security Analyst)', role: 'SECURITY_ANALYST' as const },
  RISK_ANALYST: { id: 'usr-risk-01', email: 'risk@abcbank.com', full_name: 'Rohan Mehta (Risk Analyst)', role: 'RISK_ANALYST' as const },
  EXECUTIVE: { id: 'usr-exec-01', email: 'executive@abcbank.com', full_name: 'Ananya Verma (CEO/Board)', role: 'EXECUTIVE' as const },
  AUDITOR: { id: 'usr-auditor-01', email: 'auditor@abcbank.com', full_name: 'Sanjay Joshi (Lead Auditor)', role: 'AUDITOR' as const }
};

const DEFAULT_PWD_MAP: Record<string, string> = {
  ADMIN: 'Admin@12345',
  CISO: 'Ciso@12345',
  SECURITY_ANALYST: 'Analyst@12345',
  RISK_ANALYST: 'Risk@12345',
  EXECUTIVE: 'Executive@12345',
  AUDITOR: 'Auditor@12345'
};

export const getStoredPassword = (role: string): string => {
  try {
    const custom = JSON.parse(localStorage.getItem('custom_role_passwords') || '{}');
    if (custom[role]) return custom[role];
  } catch (e) {}
  return DEFAULT_PWD_MAP[role] || 'Ciso@12345';
};

export const setStoredPassword = (role: string, newPassword: string) => {
  try {
    const custom = JSON.parse(localStorage.getItem('custom_role_passwords') || '{}');
    custom[role] = newPassword;
    localStorage.setItem('custom_role_passwords', JSON.stringify(custom));
  } catch (e) {}
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('cyber_risk_user');
    return savedUser ? JSON.parse(savedUser) : ROLE_PRESETS.CISO;
  });
  
  const [organization, setOrganization] = useState<Organization | null>({
    id: 'org-abc-bank-01',
    name: 'ABC Bank',
    industry: 'Banking & Financial Services',
    country: 'India',
    employee_count: 2500,
    annual_revenue: 5000000000.0,
    cybersecurity_budget: 10000000.0,
    risk_appetite_enterprise: 10000000.0,
    risk_appetite_critical_asset: 1000000.0,
    financial_assumptions: {}
  });

  const [token, setToken] = useState<string | null>(localStorage.getItem('cyber_risk_token'));
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!token) {
      switchRole('CISO');
    }
  }, []);

  const login = async (email: string, password?: string) => {
    setIsLoading(true);
    try {
      const foundRoleEntry = Object.entries(ROLE_PRESETS).find(([_, r]) => r.email === email);
      const roleKey = foundRoleEntry ? foundRoleEntry[0] : 'CISO';
      const actualPassword = password || getStoredPassword(roleKey);

      const res = await authService.login(email, actualPassword);
      localStorage.setItem('cyber_risk_token', res.access_token);
      localStorage.setItem('cyber_risk_user', JSON.stringify(res.user));
      setToken(res.access_token);
      setUser(res.user);
      setOrganization(res.organization);
    } catch (e) {
      const foundRole = Object.values(ROLE_PRESETS).find(r => r.email === email) || ROLE_PRESETS.CISO;
      setUser(foundRole as any);
      localStorage.setItem('cyber_risk_user', JSON.stringify(foundRole));
      throw e;
    } finally {
      setIsLoading(false);
    }
  };

  const switchRole = async (targetRole: keyof typeof ROLE_PRESETS, customPassword?: string) => {
    const preset = ROLE_PRESETS[targetRole];
    setUser(preset as any);
    try {
      const pwd = customPassword || getStoredPassword(targetRole);
      const res = await authService.login(preset.email, pwd);
      localStorage.setItem('cyber_risk_token', res.access_token);
      localStorage.setItem('cyber_risk_user', JSON.stringify(res.user));
      setToken(res.access_token);
      setUser(res.user);
      setOrganization(res.organization);
    } catch (e) {
      localStorage.setItem('cyber_risk_user', JSON.stringify(preset));
    }
  };

  const updateUserPassword = (role: string, newPassword: string) => {
    setStoredPassword(role, newPassword);
  };

  const logout = () => {
    localStorage.removeItem('cyber_risk_token');
    localStorage.removeItem('cyber_risk_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      organization, 
      token, 
      isLoading, 
      login, 
      logout, 
      switchRole, 
      updateUserPassword,
      getRolePassword: getStoredPassword 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
