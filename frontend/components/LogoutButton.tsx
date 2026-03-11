"use client";
import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  };

  return (
    <button
      onClick={logout}
      className="ml-auto text-sm text-gray-400 hover:text-gray-600 transition-colors"
    >
      Logout
    </button>
  );
}
