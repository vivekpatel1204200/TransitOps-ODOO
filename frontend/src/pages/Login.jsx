import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Truck, Lock, Mail } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("manager@transitops.in");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 via-white to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="h-12 w-12 rounded-2xl bg-brand-600 text-white flex items-center justify-center shadow-lg shadow-brand-600/30 mb-3">
            <Truck size={24} />
          </div>
          <h1 className="text-2xl font-display font-bold text-gray-900 dark:text-white">TransitOps</h1>
          <p className="text-sm text-gray-500">Smart Transport Operations Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700">
          {error && <div className="bg-red-50 text-red-600 text-sm p-2.5 rounded-lg mb-4">{error}</div>}

          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
          <div className="relative mt-1 mb-4">
            <Mail size={16} className="absolute left-3 top-3 text-gray-400" />
            <input
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-9 pr-3 py-2.5 dark:bg-gray-700 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
          <div className="relative mt-1 mb-6">
            <Lock size={16} className="absolute left-3 top-3 text-gray-400" />
            <input
              type="password"
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-9 pr-3 py-2.5 dark:bg-gray-700 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button className="w-full bg-brand-600 text-white py-2.5 rounded-lg font-semibold hover:bg-brand-700 transition-colors shadow-lg shadow-brand-600/20">
            Log In
          </button>

          <p className="text-xs text-gray-400 mt-4 text-center">
            Demo: manager@transitops.in / driver@transitops.in / safety@transitops.in / finance@transitops.in — password123
          </p>
        </form>
      </div>
    </div>
  );
}
