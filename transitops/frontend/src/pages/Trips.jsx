import { useEffect, useState } from "react";
import api from "../api/client";

const STATUS_COLORS = {
  Draft: "bg-gray-200 text-gray-700",
  Dispatched: "bg-blue-100 text-blue-700",
  Completed: "bg-green-100 text-green-700",
  Cancelled: "bg-red-100 text-red-700",
};

export default function Trips() {
  const [trips, setTrips] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [form, setForm] = useState({ source: "", destination: "", vehicle_id: "", driver_id: "", cargo_weight_kg: "", planned_distance_km: "", revenue: "" });
  const [completing, setCompleting] = useState(null);
  const [completeForm, setCompleteForm] = useState({ actual_distance_km: "", fuel_consumed_l: "" });
  const [error, setError] = useState("");

  const load = () => {
    api.get("/trips").then((res) => setTrips(res.data));
    api.get("/vehicles?dispatch_pool_only=true").then((res) => setVehicles(res.data));
    api.get("/drivers?dispatch_pool_only=true").then((res) => setDrivers(res.data));
  };
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/trips", {
        ...form,
        cargo_weight_kg: parseFloat(form.cargo_weight_kg),
        planned_distance_km: parseFloat(form.planned_distance_km),
        revenue: parseFloat(form.revenue || 0),
      });
      setForm({ source: "", destination: "", vehicle_id: "", driver_id: "", cargo_weight_kg: "", planned_distance_km: "", revenue: "" });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create trip");
    }
  };

  const dispatch = async (id) => {
    try { await api.post(`/trips/${id}/dispatch`); load(); }
    catch (err) { setError(err.response?.data?.detail || "Dispatch failed"); }
  };

  const cancel = async (id) => {
    try { await api.post(`/trips/${id}/cancel`); load(); }
    catch (err) { setError(err.response?.data?.detail || "Cancel failed"); }
  };

  const submitComplete = async (id) => {
    try {
      await api.post(`/trips/${id}/complete`, {
        actual_distance_km: parseFloat(completeForm.actual_distance_km),
        fuel_consumed_l: parseFloat(completeForm.fuel_consumed_l),
      });
      setCompleting(null);
      setCompleteForm({ actual_distance_km: "", fuel_consumed_l: "" });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Complete failed");
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Trip Management</h1>

      <form onSubmit={submit} className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow mb-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <input required placeholder="Source" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })} />
        <input required placeholder="Destination" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} />
        <select required className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600" value={form.vehicle_id}
          onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })}>
          <option value="">Select Vehicle</option>
          {vehicles.map((v) => <option key={v.id} value={v.id}>{v.registration_number} (max {v.max_load_capacity_kg}kg)</option>)}
        </select>
        <select required className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600" value={form.driver_id}
          onChange={(e) => setForm({ ...form, driver_id: e.target.value })}>
          <option value="">Select Driver</option>
          {drivers.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <input required type="number" placeholder="Cargo Weight (kg)" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.cargo_weight_kg} onChange={(e) => setForm({ ...form, cargo_weight_kg: e.target.value })} />
        <input required type="number" placeholder="Planned Distance (km)" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.planned_distance_km} onChange={(e) => setForm({ ...form, planned_distance_km: e.target.value })} />
        <input type="number" placeholder="Revenue (₹)" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.revenue} onChange={(e) => setForm({ ...form, revenue: e.target.value })} />
        <button className="col-span-2 md:col-span-4 bg-blue-600 text-white rounded p-2 font-medium hover:bg-blue-700">
          + Create Trip (Draft)
        </button>
        {error && <div className="col-span-4 text-red-600 text-sm">{error}</div>}
      </form>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 dark:bg-gray-700 text-left">
            <tr>
              <th className="p-3">Route</th><th className="p-3">Cargo</th><th className="p-3">Distance</th>
              <th className="p-3">Status</th><th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {trips.map((t) => (
              <tr key={t.id} className="border-t dark:border-gray-700">
                <td className="p-3">{t.source} → {t.destination}</td>
                <td className="p-3">{t.cargo_weight_kg} kg</td>
                <td className="p-3">{t.planned_distance_km} km</td>
                <td className="p-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[t.status]}`}>{t.status}</span></td>
                <td className="p-3 space-x-2">
                  {t.status === "Draft" && (
                    <>
                      <button onClick={() => dispatch(t.id)} className="text-blue-600 text-xs font-semibold hover:underline">Dispatch</button>
                      <button onClick={() => cancel(t.id)} className="text-red-600 text-xs font-semibold hover:underline">Cancel</button>
                    </>
                  )}
                  {t.status === "Dispatched" && (
                    <>
                      <button onClick={() => setCompleting(completing === t.id ? null : t.id)} className="text-green-600 text-xs font-semibold hover:underline">Complete</button>
                      <button onClick={() => cancel(t.id)} className="text-red-600 text-xs font-semibold hover:underline">Cancel</button>
                    </>
                  )}
                  {completing === t.id && (
                    <div className="mt-2 flex gap-2 items-center">
                      <input type="number" placeholder="Actual km" className="border rounded p-1 text-xs w-24 dark:bg-gray-700 dark:border-gray-600"
                        value={completeForm.actual_distance_km} onChange={(e) => setCompleteForm({ ...completeForm, actual_distance_km: e.target.value })} />
                      <input type="number" placeholder="Fuel (L)" className="border rounded p-1 text-xs w-20 dark:bg-gray-700 dark:border-gray-600"
                        value={completeForm.fuel_consumed_l} onChange={(e) => setCompleteForm({ ...completeForm, fuel_consumed_l: e.target.value })} />
                      <button onClick={() => submitComplete(t.id)} className="bg-green-600 text-white text-xs px-2 py-1 rounded">Save</button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
