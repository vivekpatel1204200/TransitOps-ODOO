import { Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "./context/AuthContext";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Vehicles from "./pages/Vehicles";
import Drivers from "./pages/Drivers";
import Trips from "./pages/Trips";
import LiveMap from "./pages/LiveMap";
import Analytics from "./pages/Analytics";
import NotificationToasts from "./components/NotificationToasts";

function Protected({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function Layout({ children }) {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar dark={dark} setDark={setDark} />
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">{children}</main>
      </div>
      <NotificationToasts />
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
