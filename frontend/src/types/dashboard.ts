import type { Scan, Vulnerability } from "./scan";

export interface SeverityBreakdown {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface TrendPoint {
  date: string;
  vulnerability_count: number;
}

export interface DashboardSummary {
  overall_security_score: number | null;
  total_projects: number;
  total_scans: number;
  severity_breakdown: SeverityBreakdown;
  recent_scans: Scan[];
  critical_issues: Vulnerability[];
  trend: TrendPoint[];
}
