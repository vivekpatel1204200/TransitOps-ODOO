import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import api, { API_URL } from "../api/client";

export default function Analytics() {
  const [perf, setPerf] = useState([]);
  const [predictive, setPredictive] = useState([]);
  const [dispatch, setDispatch] = useState([]);

  useEffect(() => {
    api.get("/analytics/vehicle-performance").then((res) => setPerf(res.data));
    api.get("/predictive-maintenance").then((res) => setPredictive(res.data));
    api.get("/analytics/smart-dispatch").then((res) => setDispatch(res.data));
  }, []);

  const exportCsv = () => {
    window.open(`${API_URL}/analytics/export/csv`, "_blank");
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Reports & Analytics</h1>
        <button onClick={exportCsv} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
          Export CSV
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <h2 className="font-semibold mb-3">Vehicle ROI</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={perf}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="registration_number" fontSize={11} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="roi" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <h2 className="font-semibold mb-3">🔧 Predictive Maintenance (AI Risk Score)</h2>
        <table className="w-full text-sm">
          <thead className="text-left text-gray-500">
            <tr><th className="p-2">Vehicle</th><th className="p-2">Risk Score</th><th className="p-2">Recommendation</th></tr>
          </thead>
          <tbody>
            {predictive.map((p) => (
              <tr key={p.vehicle_id} className="border-t dark:border-gray-700">
                <td className="p-2">{p.registration_number}</td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${p.risk_score > 65 ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
                    {p.risk_score}
                  </span>
                </td>
                <td className="p-2">{p.recommendation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <h2 className="font-semibold mb-3">🎯 Smart Dispatch Suggestions (lowest cost/km first)</h2>
        <table className="w-full text-sm">
          <thead className="text-left text-gray-500">
            <tr><th className="p-2">Rank</th><th className="p-2">Vehicle</th><th className="p-2">Cost per KM</th></tr>
          </thead>
          <tbody>
            {dispatch.map((d, i) => (
              <tr key={d.vehicle_id} className="border-t dark:border-gray-700">
                <td className="p-2">#{i + 1}</td>
                <td className="p-2">{d.registration_number}</td>
                <td className="p-2">₹{d.cost_per_km}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
