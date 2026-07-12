import { Moon, Sun, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar({ dark, setDark }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-16 sticky top-0 z-40 flex items-center justify-between px-6 bg-white/80 dark:bg-gray-800/80 backdrop-blur border-b border-gray-200 dark:border-gray-700">
      <div />
      <div className="flex items-center gap-3">
        <button
          onClick={() => setDark(!dark)}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
          title="Toggle dark mode"
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        {user && (
          <>
            <span className="text-sm font-medium capitalize px-3 py-1.5 rounded-full bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-500">
              {user.role?.replace("_", " ")}
            </span>
            <button
              onClick={() => { logout(); navigate("/login"); }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300 text-sm font-medium hover:bg-red-100 dark:hover:bg-red-900/50"
            >
              <LogOut size={14} /> Logout
            </button>
          </>
        )}
      </div>
    </header>
  );
}
