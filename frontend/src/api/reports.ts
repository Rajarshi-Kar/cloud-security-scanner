import { apiClient } from "./client";
import type { Report, ReportFormat } from "../types/report";

export async function listReports(scanId: string): Promise<Report[]> {
  const { data } = await apiClient.get<Report[]>(`/scans/${scanId}/reports`);
  return data;
}

export async function createReport(scanId: string, format: ReportFormat): Promise<Report> {
  const { data } = await apiClient.post<Report>(`/scans/${scanId}/reports`, { format });
  return data;
}

export async function downloadReport(reportId: string, filename: string): Promise<void> {
  const response = await apiClient.get(`/reports/${reportId}/download`, { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}
