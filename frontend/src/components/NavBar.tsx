import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded px-3 py-1.5 text-sm font-medium ${isActive ? "bg-slate-800 text-white" : "text-slate-600 hover:bg-slate-100"}`;

  return (
    <nav className="flex items-center justify-between border-b bg-white px-8 py-3">
      <div className="flex items-center gap-2">
        <span className="mr-4 font-semibold text-slate-800">Cloud Security Scanner</span>
        <NavLink to="/dashboard" className={linkClass}>
          Dashboard
        </NavLink>
        <NavLink to="/projects" className={linkClass}>
          Projects
        </NavLink>
      </div>
      <div className="flex items-center gap-3 text-sm text-slate-600">
        <span>
          {user?.full_name} ({user?.role})
        </span>
        <button onClick={logout} className="rounded bg-slate-200 px-3 py-1">
          Logout
        </button>
      </div>
    </nav>
  );
}
