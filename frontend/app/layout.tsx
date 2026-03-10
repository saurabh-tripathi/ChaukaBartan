import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "ChaukaBartan",
  description: "Task, Goal & Habit Tracker",
};

const navLinks = [
  { href: "/", label: "Dashboard" },
  { href: "/goals", label: "Goals" },
  { href: "/tasks", label: "Tasks" },
  { href: "/habits", label: "Habits" },
  { href: "/plans", label: "Plans" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
          <span className="font-bold text-lg text-indigo-600">ChaukaBartan</span>
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} className="text-sm text-gray-600 hover:text-indigo-600 transition-colors">
              {l.label}
            </Link>
          ))}
        </nav>
        <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
