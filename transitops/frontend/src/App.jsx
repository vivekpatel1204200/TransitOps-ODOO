import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Vehicles from "./pages/Vehicles";
import Drivers from "./pages/Drivers";
import Trips from "./pages/Trips";
import LiveMap from "./pages/LiveMap";
import Analytics from "./pages/Analytics";

function Protected({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dark, setDark] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const navItem = "px-3 py-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 text-sm font-medium";

  return (
    <div className="min-h-screen">
      <nav className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <span className="text-xl font-bold text-blue-600">🚚 TransitOps</span>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/" className={navItem}>Dashboard</Link>
          <Link to="/vehicles" className={navItem}>Vehicles</Link>
          <Link to="/drivers" className={navItem}>Drivers</Link>
          <Link to="/trips" className={navItem}>Trips</Link>
          <Link to="/live-map" className={navItem}>Live Map</Link>
          <Link to="/analytics" className={navItem}>Analytics</Link>
          <button onClick={() => setDark(!dark)} className={navItem}>{dark ? "☀️" : "🌙"}</button>
          {user && (
            <button
              onClick={() => { logout(); navigate("/login"); }}
              className="px-3 py-2 rounded-lg bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300 text-sm font-medium"
            >
              Logout ({user.role})
            </button>
          )}
        </div>
      </nav>
      <main className="p-6 max-w-7xl mx-auto">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><Layout><Dashboard /></Layout></Protected>} />
      <Route path="/vehicles" element={<Protected><Layout><Vehicles /></Layout></Protected>} />
      <Route path="/drivers" element={<Protected><Layout><Drivers /></Layout></Protected>} />
      <Route path="/trips" element={<Protected><Layout><Trips /></Layout></Protected>} />
      <Route path="/live-map" element={<Protected><Layout><LiveMap /></Layout></Protected>} />
      <Route path="/analytics" element={<Protected><Layout><Analytics /></Layout></Protected>} />
    </Routes>
  );
}
