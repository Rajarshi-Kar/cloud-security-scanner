import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { ChangeEvent, FormEvent } from "react";
import { useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getProject } from "../api/projects";
import { createScan, listScans, uploadDockerImageScan } from "../api/scans";
import Layout from "../components/Layout";
import SeverityBadge from "../components/SeverityBadge";

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const queryClient = useQueryClient();

  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => getProject(projectId!),
    enabled: !!projectId,
  });

  const { data: scans, isLoading } = useQuery({
    queryKey: ["scans", projectId],
    queryFn: () => listScans(projectId!),
    enabled: !!projectId,
    refetchInterval: 5000,
  });

  const [repoTarget, setRepoTarget] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const repoScanMutation = useMutation({
    mutationFn: () => createScan(projectId!, "repository", repoTarget),
    onSuccess: () => {
      setRepoTarget("");
      queryClient.invalidateQueries({ queryKey: ["scans", projectId] });
    },
  });

  const dockerScanMutation = useMutation({
    mutationFn: (file: File) => uploadDockerImageScan(projectId!, file),
    onSuccess: () => {
      if (fileInputRef.current) fileInputRef.current.value = "";
      queryClient.invalidateQueries({ queryKey: ["scans", projectId] });
    },
  });

  function handleRepoScanSubmit(e: FormEvent) {
    e.preventDefault();
    if (!repoTarget.trim()) return;
    repoScanMutation.mutate();
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) dockerScanMutation.mutate(file);
  }

  if (!projectId) return null;

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-slate-800">{project?.name ?? "Project"}</h1>
      {project?.repo_url && <p className="text-sm text-slate-500">{project.repo_url}</p>}

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-lg bg-white p-4 shadow">
          <p className="mb-2 text-sm font-medium text-slate-600">Scan a repository</p>
          <form onSubmit={handleRepoScanSubmit} className="flex gap-2">
            <input
              value={repoTarget}
              onChange={(e) => setRepoTarget(e.target.value)}
              placeholder="https://github.com/org/repo.git"
              className="flex-1 rounded border px-3 py-2 text-sm"
              required
            />
            <button
              type="submit"
              disabled={repoScanMutation.isPending}
              className="rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700 disabled:opacity-50"
            >
              {repoScanMutation.isPending ? "Queuing..." : "Scan"}
            </button>
          </form>
        </div>

        <div className="rounded-lg bg-white p-4 shadow">
          <p className="mb-2 text-sm font-medium text-slate-600">
            Scan a Docker image (upload a `docker save` .tar)
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".tar"
            onChange={handleFileChange}
            disabled={dockerScanMutation.isPending}
            className="text-sm"
          />
          {dockerScanMutation.isPending && <p className="mt-2 text-xs text-slate-500">Uploading...</p>}
        </div>
      </div>

      <div className="mt-6 rounded-lg bg-white p-4 shadow">
        <p className="mb-2 text-sm font-medium text-slate-600">Scans</p>
        {isLoading && <p className="text-sm text-slate-500">Loading scans...</p>}
        <ul className="divide-y divide-slate-100">
          {scans?.map((scan) => (
            <li key={scan.id} className="flex items-center justify-between py-2 text-sm">
              <Link to={`/scans/${scan.id}`} className="truncate text-slate-700 hover:underline">
                [{scan.scan_type}] {scan.target}
              </Link>
              <div className="flex items-center gap-2">
                {scan.security_score !== null && (
                  <span className="text-xs text-slate-400">{scan.security_score}/100</span>
                )}
                <SeverityBadge label={scan.status} />
              </div>
            </li>
          ))}
          {scans?.length === 0 && <li className="py-2 text-sm text-slate-400">No scans yet.</li>}
        </ul>
      </div>
    </Layout>
  );
}
