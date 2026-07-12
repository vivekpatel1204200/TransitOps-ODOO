import { useEffect, useState } from "react";
import api from "../api/client";

const CARD_STYLES = [
  "from-blue-500 to-blue-600",
  "from-green-500 to-green-600",
  "from-amber-500 to-amber-600",
  "from-purple-500 to-purple-600",
  "from-red-500 to-red-600",
  "from-teal-500 to-teal-600",
  "from-pink-500 to-pink-600",
];

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    api.get("/analytics/dashboard").then((res) => setKpis(res.data));
  }, []);

  if (!kpis) return <div className="text-gray-500">Loading dashboard…</div>;

  const cards = [
    { label: "Active Vehicles", value: kpis.active_vehicles },
    { label: "Available Vehicles", value: kpis.available_vehicles },
    { label: "In Maintenance", value: kpis.vehicles_in_maintenance },
    { label: "Active Trips", value: kpis.active_trips },
    { label: "Pending Trips", value: kpis.pending_trips },
    { label: "Drivers On Duty", value: kpis.drivers_on_duty },
    { label: "Fleet Utilization", value: `${kpis.fleet_utilization_pct}%` },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Operations Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {cards.map((c, i) => (
          <div
            key={c.label}
            className={`bg-gradient-to-br ${CARD_STYLES[i % CARD_STYLES.length]} text-white rounded-2xl p-5 shadow-lg`}
          >
            <p className="text-sm opacity-90">{c.label}</p>
            <p className="text-3xl font-bold mt-1">{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
