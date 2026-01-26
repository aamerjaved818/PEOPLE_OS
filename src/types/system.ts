import { ConfigValue } from './shared';

export interface SystemLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  details: string;
  level: 'Info' | 'Warning' | 'Error';
}

export interface AuditLog {
  id: string;
  user: string;
  action: string;
  time: string;
  status: 'Hashed' | 'Flagged' | 'Success' | 'Warning' | 'Error' | 'Info';
}

export interface BusinessRule {
  id: string;
  name: string;
  description: string;
  condition: string;
  action: string;
  isActive: boolean;
}

export type TabId = string;

export interface SystemFlags {
  mfa_enforced: boolean;
  biometrics_required: boolean;
  ip_whitelisting: boolean;
  session_timeout: string;
  password_complexity: string;
  session_isolation: boolean;
  neural_bypass: boolean;
  api_caching: boolean;
  debug_mode: boolean;
  immutable_logs: boolean;
}

export interface NotificationSettings {
  email: {
    smtpServer: string;
    port: number;
    username: string;
    password: string;
    fromAddress: string;
  };
  sms: { provider: string; apiKey: string; senderId: string };
}

export interface AISettings {
  status: 'online' | 'offline';
  provider: 'gemini' | 'openai' | 'anthropic';
  apiKeys: { gemini: string; openai: string; anthropic: string };
  agents: { resume_screener: boolean; turnover_predictor: boolean; chat_assistant: boolean };
}

export interface ApiKey {
  id: string;
  name: string;
  key: string;
  scope: string;
  created: string;
  lastUsed: string;
  status: 'Active' | 'Revoked';
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  status: 'Active' | 'Inactive';
  lastTriggered: string;
  secret: string;
}

export interface ComplianceResult {
  id: string;
  type: 'Success' | 'Warning' | 'Error';
  message: string;
  timestamp: string;
}

export interface RbacRow {
  module: string;
  perms: boolean[];
}

export type SettingScope = 'SYSTEM' | 'ORGANIZATION' | 'MODULE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type SettingType = 'toggle' | 'text' | 'select' | 'number' | 'json';

export interface SettingNode {
  id: string;
  key: string;
  label: string;
  category: string;
  value: ConfigValue;
  defaultValue: any;
  type: SettingType;
  options?: string[];
  scope: SettingScope;
  isOverridden: boolean;
  inheritedFrom?: SettingScope;
  riskLevel: RiskLevel;
  description: string;
  lastUpdated: string;
  updatedBy: string;
  impact?: string;
}

export interface AISuggestion {
  id: string;
  type: 'designation' | 'grade' | 'department' | 'salary' | 'general';
  field: string;
  suggestedValue: string;
  currentValue?: string;
  confidence: number; // 0-100
  reasoning?: string;
  metadata?: Record<string, unknown>;
}
