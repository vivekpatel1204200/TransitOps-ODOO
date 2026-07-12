import { useState } from "react";
import { useNavigate } from "react-router-dom";
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl w-96">
        <h1 className="text-2xl font-bold mb-1 text-blue-600">🚚 TransitOps</h1>
        <p className="text-sm text-gray-500 mb-6">Smart Transport Operations Platform</p>

        {error && <div className="bg-red-50 text-red-600 text-sm p-2 rounded mb-4">{error}</div>}

        <label className="text-sm font-medium">Email</label>
        <input
          className="w-full border rounded-lg p-2 mb-4 mt-1 dark:bg-gray-700 dark:border-gray-600"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="text-sm font-medium">Password</label>
        <input
          type="password"
          className="w-full border rounded-lg p-2 mb-6 mt-1 dark:bg-gray-700 dark:border-gray-600"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700">
          Login
        </button>

        <p className="text-xs text-gray-400 mt-4">
          Seeded demo logins: manager@transitops.in / driver@transitops.in / safety@transitops.in / finance@transitops.in — password123
        </p>
      </form>
    </div>
  );
}
