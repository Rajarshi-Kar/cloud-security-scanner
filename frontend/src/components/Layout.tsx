import type { ReactNode } from "react";

import NavBar from "./NavBar";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <div className="p-8">{children}</div>
    </div>
  );
}
