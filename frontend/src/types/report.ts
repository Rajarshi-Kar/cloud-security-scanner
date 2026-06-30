export type ReportFormat = "pdf" | "json";

export interface Report {
  id: string;
  scan_id: string;
  format: ReportFormat;
  file_path: string;
  created_at: string;
}
