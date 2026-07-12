import { useEffect, useState } from "react";
import { Plus, Truck } from "lucide-react";
import api from "../api/client";

const STATUS_COLORS = {
  Available: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  "On Trip": "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  "In Shop": "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  Retired: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
};

export default function Vehicles() {
  const [vehicles, setVehicles] = useState([]);
  const [form, setForm] = useState({
    registration_number: "", name_model: "", type: "Van",
    max_load_capacity_kg: "", acquisition_cost: "", region: "Ahmedabad",
  });
  const [error, setError] = useState("");

  const load = () => api.get("/vehicles").then((res) => setVehicles(res.data));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/vehicles", {
        ...form,
        max_load_capacity_kg: parseFloat(form.max_load_capacity_kg),
        acquisition_cost: parseFloat(form.acquisition_cost),
      });
      setForm({ ...form, registration_number: "", name_model: "", max_load_capacity_kg: "", acquisition_cost: "" });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add vehicle");
    }
  };

  const inputCls = "border border-gray-300 dark:border-gray-600 rounded-lg p-2.5 dark:bg-gray-700 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none text-sm";

  return (
    <div>
      <div className="flex items-center gap-2 mb-6">
        <Truck className="text-brand-600" size={22} />
        <h1 className="text-2xl font-display font-bold">Vehicle Registry</h1>
      </div>

      <form onSubmit={submit} className="bg-white dark:bg-gray-800 p-5 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 mb-6 grid grid-cols-2 md:grid-cols-6 gap-3">
        <input required placeholder="Reg. Number (GJ-01-AB-1234)" className={`${inputCls} col-span-2`}
          value={form.registration_number} onChange={(e) => setForm({ ...form, registration_number: e.target.value })} />
        <input required placeholder="Model" className={inputCls}
          value={form.name_model} onChange={(e) => setForm({ ...form, name_model: e.target.value })} />
        <select className={inputCls} value={form.type}
          onChange={(e) => setForm({ ...form, type: e.target.value })}>
          {["Van", "Truck", "Mini-Truck", "Container Truck"].map((t) => <option key={t}>{t}</option>)}
        </select>
        <input required type="number" placeholder="Max Load (kg)" className={inputCls}
          value={form.max_load_capacity_kg} onChange={(e) => setForm({ ...form, max_load_capacity_kg: e.target.value })} />
        <input required type="number" placeholder="Acquisition Cost (₹)" className={inputCls}
          value={form.acquisition_cost} onChange={(e) => setForm({ ...form, acquisition_cost: e.target.value })} />
        <button className="col-span-2 md:col-span-6 flex items-center justify-center gap-1.5 bg-brand-600 text-white rounded-lg p-2.5 font-medium hover:bg-brand-700 transition-colors">
          <Plus size={16} /> Add Vehicle
        </button>
        {error && <div className="col-span-6 text-red-600 text-sm">{error}</div>}
      </form>

      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-700/50 text-left text-gray-500 dark:text-gray-400 uppercase text-xs tracking-wide">
            <tr>
              <th className="p-3">Reg. Number</th><th className="p-3">Model</th><th className="p-3">Type</th>
              <th className="p-3">Max Load</th><th className="p-3">Odometer</th><th className="p-3">Region</th><th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map((v) => (
              <tr key={v.id} className="border-t border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <td className="p-3 font-medium">{v.registration_number}</td>
                <td className="p-3">{v.name_model}</td>
                <td className="p-3">{v.type}</td>
                <td className="p-3">{v.max_load_capacity_kg} kg</td>
                <td className="p-3">{v.odometer_km} km</td>
                <td className="p-3">{v.region}</td>
                <td className="p-3"><span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[v.status]}`}>{v.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
