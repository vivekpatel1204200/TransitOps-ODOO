import { useEffect, useState } from "react";
import api from "../api/client";

const STATUS_COLORS = {
  Available: "bg-green-100 text-green-700",
  "On Trip": "bg-blue-100 text-blue-700",
  "Off Duty": "bg-gray-200 text-gray-600",
  Suspended: "bg-red-100 text-red-700",
};

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);
  const [form, setForm] = useState({
    name: "", license_number: "", license_category: "LMV",
    license_expiry_date: "", contact_number: "",
  });
  const [error, setError] = useState("");

  const load = () => api.get("/drivers").then((res) => setDrivers(res.data));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/drivers", { ...form, license_expiry_date: new Date(form.license_expiry_date).toISOString() });
      setForm({ name: "", license_number: "", license_category: "LMV", license_expiry_date: "", contact_number: "" });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add driver");
    }
  };

  const isExpired = (d) => new Date(d) <= new Date();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Driver Management</h1>

      <form onSubmit={submit} className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow mb-6 grid grid-cols-2 md:grid-cols-5 gap-3">
        <input required placeholder="Name" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input required placeholder="License Number" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.license_number} onChange={(e) => setForm({ ...form, license_number: e.target.value })} />
        <select className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600" value={form.license_category}
          onChange={(e) => setForm({ ...form, license_category: e.target.value })}>
          {["LMV", "HMV", "LMV-TR"].map((c) => <option key={c}>{c}</option>)}
        </select>
        <input required type="date" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.license_expiry_date} onChange={(e) => setForm({ ...form, license_expiry_date: e.target.value })} />
        <input required placeholder="Contact Number" className="border rounded p-2 dark:bg-gray-700 dark:border-gray-600"
          value={form.contact_number} onChange={(e) => setForm({ ...form, contact_number: e.target.value })} />
        <button className="col-span-2 md:col-span-5 bg-blue-600 text-white rounded p-2 font-medium hover:bg-blue-700">
          + Add Driver
        </button>
        {error && <div className="col-span-5 text-red-600 text-sm">{error}</div>}
      </form>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 dark:bg-gray-700 text-left">
            <tr>
              <th className="p-3">Name</th><th className="p-3">License</th><th className="p-3">Category</th>
              <th className="p-3">Expiry</th><th className="p-3">Safety Score</th><th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {drivers.map((d) => (
              <tr key={d.id} className="border-t dark:border-gray-700">
                <td className="p-3 font-medium">{d.name}</td>
                <td className="p-3">{d.license_number}</td>
                <td className="p-3">{d.license_category}</td>
                <td className={`p-3 ${isExpired(d.license_expiry_date) ? "text-red-600 font-semibold" : ""}`}>
                  {new Date(d.license_expiry_date).toLocaleDateString()}
                  {isExpired(d.license_expiry_date) && " (Expired)"}
                </td>
                <td className="p-3">{d.safety_score}</td>
                <td className="p-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[d.status]}`}>{d.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
