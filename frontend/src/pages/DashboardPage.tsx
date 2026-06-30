import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { fetchDashboardSummary } from "../api/dashboard";
import Layout from "../components/Layout";
import SeverityBadge from "../components/SeverityBadge";

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary,
  });

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-slate-800">Dashboard</h1>

      {isLoading && <p className="mt-6 text-slate-500">Loading dashboard...</p>}
      {isError && <p className="mt-6 text-red-600">Failed to load dashboard.</p>}

      {data && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard
              label="Security Score"
              value={data.overall_security_score !== null ? `${data.overall_security_score}/100` : "—"}
            />
            <StatCard label="Total Projects" value={String(data.total_projects)} />
            <StatCard label="Total Scans" value={String(data.total_scans)} />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ChartCard title="Vulnerability Trend (14 days)">
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data.trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Line type="monotone" dataKey="vulnerability_count" stroke="#1e293b" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Findings by Severity">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart
                  data={Object.entries(data.severity_breakdown).map(([severity, count]) => ({
                    severity,
                    count,
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="severity" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#b91c1c" />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ChartCard title="Recent Scans">
              <ul className="divide-y divide-slate-100">
                {data.recent_scans.map((scan) => (
                  <li key={scan.id} className="flex items-center justify-between py-2 text-sm">
                    <span className="truncate text-slate-700">{scan.target}</span>
                    <SeverityBadge label={scan.status} />
                  </li>
                ))}
                {data.recent_scans.length === 0 && (
                  <li className="py-2 text-sm text-slate-400">No scans yet.</li>
                )}
              </ul>
            </ChartCard>

            <ChartCard title="Critical Issues">
              <ul className="divide-y divide-slate-100">
                {data.critical_issues.map((vuln) => (
                  <li key={vuln.id} className="flex items-center justify-between py-2 text-sm">
                    <span className="truncate text-slate-700">{vuln.title}</span>
                    <SeverityBadge label={vuln.severity} />
                  </li>
                ))}
                {data.critical_issues.length === 0 && (
                  <li className="py-2 text-sm text-slate-400">No critical issues.</li>
                )}
              </ul>
            </ChartCard>
          </div>
        </div>
      )}
    </Layout>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-800">{value}</p>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <p className="mb-2 text-sm font-medium text-slate-600">{title}</p>
      {children}
    </div>
  );
}
