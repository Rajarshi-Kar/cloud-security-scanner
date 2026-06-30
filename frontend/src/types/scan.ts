export type ScanType = "repository" | "docker_image";
export type ScanStatus = "pending" | "running" | "completed" | "failed";
export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface Scan {
  id: string;
  project_id: string;
  scan_type: ScanType;
  status: ScanStatus;
  target: string;
  security_score: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface Vulnerability {
  id: string;
  scan_id: string;
  source: string;
  severity: Severity;
  title: string;
  description: string | null;
  cve_id: string | null;
  package_name: string | null;
  file_path: string | null;
  created_at: string;
}
