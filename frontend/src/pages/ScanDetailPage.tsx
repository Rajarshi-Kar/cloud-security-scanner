import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { createReport, downloadReport, listReports } from "../api/reports";
import { getScan, listVulnerabilities } from "../api/scans";
import Layout from "../components/Layout";
import SeverityBadge from "../components/SeverityBadge";
import type { Severity } from "../types/scan";

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low", "info"];

export default function ScanDetailPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const queryClient = useQueryClient();

  const { data: scan } = useQuery({
    queryKey: ["scan", scanId],
    queryFn: () => getScan(scanId!),
    enabled: !!scanId,
    refetchInterval: (query) => (query.state.data?.status === "completed" || query.state.data?.status === "failed" ? false : 4000),
  });

  const { data: vulnerabilities } = useQuery({
    queryKey: ["vulnerabilities", scanId],
    queryFn: () => listVulnerabilities(scanId!),
    enabled: !!scanId && scan?.status === "completed",
  });

  const { data: reports } = useQuery({
    queryKey: ["reports", scanId],
    queryFn: () => listReports(scanId!),
    enabled: !!scanId,
  });

  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<Severity | "all">("all");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const filtered = useMemo(() => {
    if (!vulnerabilities) return [];
    return vulnerabilities
      .filter((v) => severityFilter === "all" || v.severity === severityFilter)
      .filter((v) => {
        const q = search.toLowerCase();
        return (
          !q ||
          v.title.toLowerCase().includes(q) ||
          (v.package_name ?? "").toLowerCase().includes(q) ||
          (v.cve_id ?? "").toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        return sortDir === "asc" ? diff : -diff;
      });
  }, [vulnerabilities, search, severityFilter, sortDir]);

  const reportMutation = useMutation({
    mutationFn: (format: "pdf" | "json") => createReport(scanId!, format),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reports", scanId] }),
  });

  if (!scanId) return null;

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-slate-800">Scan Detail</h1>
      {scan && (
        <div className="mt-2 flex items-center gap-3 text-sm text-slate-600">
          <span className="truncate">{scan.target}</span>
          <SeverityBadge label={scan.status} />
          {scan.security_score !== null && <span>{scan.security_score}/100</span>}
        </div>
      )}

      {scan?.status === "completed" && (
        <div className="mt-6 rounded-lg bg-white p-4 shadow">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search title, package, CVE..."
              className="flex-1 rounded border px-3 py-2 text-sm"
            />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as Severity | "all")}
              className="rounded border px-2 py-2 text-sm"
            >
              <option value="all">All severities</option>
              {SEVERITIES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <button
              onClick={() => setSortDir((d) => (d === "asc" ? "desc" : "asc"))}
              className="rounded border px-3 py-2 text-sm text-slate-600"
            >
              Date {sortDir === "asc" ? "↑" : "↓"}
            </button>
          </div>

          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b text-xs uppercase text-slate-400">
                <th className="py-2">Severity</th>
                <th className="py-2">Title</th>
                <th className="py-2">Package</th>
                <th className="py-2">CVE</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((v) => (
                <tr key={v.id} className="border-b border-slate-100">
                  <td className="py-2">
                    <SeverityBadge label={v.severity} />
                  </td>
                  <td className="py-2">{v.title}</td>
                  <td className="py-2 text-slate-500">{v.package_name ?? "-"}</td>
                  <td className="py-2">
                    {v.cve_id ? (
                      <a
                        href={`https://nvd.nist.gov/vuln/detail/${v.cve_id}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {v.cve_id}
                      </a>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={4} className="py-4 text-center text-slate-400">
                    No matching findings.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6 rounded-lg bg-white p-4 shadow">
        <p className="mb-2 text-sm font-medium text-slate-600">Reports</p>
        <div className="mb-3 flex gap-2">
          <button
            onClick={() => reportMutation.mutate("json")}
            disabled={scan?.status !== "completed" || reportMutation.isPending}
            className="rounded bg-slate-800 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          >
            Generate JSON
          </button>
          <button
            onClick={() => reportMutation.mutate("pdf")}
            disabled={scan?.status !== "completed" || reportMutation.isPending}
            className="rounded bg-slate-800 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          >
            Generate PDF
          </button>
        </div>
        <ul className="divide-y divide-slate-100">
          {reports?.map((r) => (
            <li key={r.id} className="flex items-center justify-between py-2 text-sm">
              <span className="uppercase text-slate-600">{r.format}</span>
              <button
                onClick={() => downloadReport(r.id, `scan-report-${scan?.id}.${r.format}`)}
                className="text-blue-600 hover:underline"
              >
                Download
              </button>
            </li>
          ))}
          {reports?.length === 0 && <li className="py-2 text-sm text-slate-400">No reports yet.</li>}
        </ul>
      </div>
    </Layout>
  );
}
