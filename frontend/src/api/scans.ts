import { apiClient } from "./client";
import type { Scan, ScanType, Vulnerability } from "../types/scan";

export async function listScans(projectId: string): Promise<Scan[]> {
  const { data } = await apiClient.get<Scan[]>(`/projects/${projectId}/scans`);
  return data;
}

export async function getScan(scanId: string): Promise<Scan> {
  const { data } = await apiClient.get<Scan>(`/scans/${scanId}`);
  return data;
}

export async function createScan(
  projectId: string,
  scan_type: ScanType,
  target: string,
): Promise<Scan> {
  const { data } = await apiClient.post<Scan>(`/projects/${projectId}/scans`, { scan_type, target });
  return data;
}

export async function uploadDockerImageScan(projectId: string, file: File): Promise<Scan> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<Scan>(`/projects/${projectId}/scans/docker-image`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listVulnerabilities(scanId: string): Promise<Vulnerability[]> {
  const { data } = await apiClient.get<Vulnerability[]>(`/scans/${scanId}/vulnerabilities`);
  return data;
}
