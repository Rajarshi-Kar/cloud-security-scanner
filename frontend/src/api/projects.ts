import { apiClient } from "./client";
import type { Project } from "../types/project";

export async function listProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/projects");
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await apiClient.get<Project>(`/projects/${id}`);
  return data;
}

export async function createProject(name: string, repo_url?: string): Promise<Project> {
  const { data } = await apiClient.post<Project>("/projects", { name, repo_url: repo_url || null });
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await apiClient.delete(`/projects/${id}`);
}
