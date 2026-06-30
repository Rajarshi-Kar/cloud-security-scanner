import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { FormEvent } from "react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { createProject, listProjects } from "../api/projects";
import Layout from "../components/Layout";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const { data: projects, isLoading } = useQuery({ queryKey: ["projects"], queryFn: listProjects });

  const [name, setName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");

  const createMutation = useMutation({
    mutationFn: () => createProject(name, repoUrl),
    onSuccess: () => {
      setName("");
      setRepoUrl("");
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    createMutation.mutate();
  }

  return (
    <Layout>
      <h1 className="text-2xl font-semibold text-slate-800">Projects</h1>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-wrap gap-2 rounded-lg bg-white p-4 shadow">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project name"
          className="flex-1 rounded border px-3 py-2 text-sm"
          required
        />
        <input
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="Repo URL (optional)"
          className="flex-1 rounded border px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {createMutation.isPending ? "Creating..." : "New Project"}
        </button>
      </form>

      {isLoading && <p className="mt-6 text-slate-500">Loading projects...</p>}

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects?.map((project) => (
          <Link
            key={project.id}
            to={`/projects/${project.id}`}
            className="rounded-lg bg-white p-4 shadow hover:shadow-md"
          >
            <p className="font-medium text-slate-800">{project.name}</p>
            <p className="mt-1 truncate text-xs text-slate-500">{project.repo_url || "No repo URL"}</p>
          </Link>
        ))}
        {projects?.length === 0 && <p className="text-sm text-slate-400">No projects yet.</p>}
      </div>
    </Layout>
  );
}
