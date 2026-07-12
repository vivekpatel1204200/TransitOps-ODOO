import { useEffect, useState } from "react";
import { Truck, CheckCircle2, Wrench, Route, Clock, Users, Gauge, ShieldAlert, IndianRupee, Award } from "lucide-react";
import api from "../api/client";

const Card = ({ label, value, icon: Icon, tint }) => (
  <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
    <div className={`h-10 w-10 rounded-xl flex items-center justify-center mb-3 ${tint}`}>
      <Icon size={20} />
    </div>
    <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
    <p className="text-3xl font-display font-bold mt-1">{value ?? "—"}</p>
  </div>
);

function FleetManagerView({ d }) {
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <Card label="Active Vehicles" value={d.active_vehicles} icon={Truck} tint="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" />
        <Card label="Available Vehicles" value={d.available_vehicles} icon={CheckCircle2} tint="bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400" />
        <Card label="In Maintenance" value={d.vehicles_in_maintenance} icon={Wrench} tint="bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400" />
        <Card label="Active Trips" value={d.active_trips} icon={Route} tint="bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400" />
        <Card label="Pending Trips" value={d.pending_trips} icon={Clock} tint="bg-orange-50 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400" />
        <Card label="Drivers On Duty" value={d.drivers_on_duty} icon={Users} tint="bg-teal-50 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400" />
      </div>
      <div className="bg-gradient-to-br from-brand-600 to-brand-700 text-white rounded-2xl p-6 shadow-lg flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 text-brand-100 mb-1"><Gauge size={16} /><span className="text-sm font-medium">Fleet Utilization</span></div>
          <p className="text-4xl font-display font-bold">{d.fleet_utilization_pct}%</p>
        </div>
        <div className="h-16 w-16 rounded-full border-4 border-white/30 flex items-center justify-center text-sm font-semibold">{d.fleet_utilization_pct}%</div>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 className="font-semibold mb-3">Recent Trips</h3>
        <div className="space-y-2">
          {(d.recent_trips || []).map((t) => (
            <div key={t.id} className="flex justify-between text-sm border-b border-gray-100 dark:border-gray-700 pb-2">
              <span>{t.source} → {t.destination}</span>
              <span className="text-gray-500 capitalize">{t.status}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function DriverView({ d }) {
  if (!d.linked) return <div className="text-gray-500">{d.message}</div>;
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <Card label="Safety Score" value={d.safety_score} icon={Award} tint="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" />
        <Card label="Completed Trips" value={d.completed_trip_count} icon={Route} tint="bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400" />
        <Card label="Total Distance (km)" value={d.total_distance_km} icon={Gauge} tint="bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400" />
      </div>
      {d.license_expired && <div className="bg-red-50 text-red-600 rounded-xl p-3 mb-4 text-sm">Your license expired. Renew it immediately.</div>}
      {!d.license_expired && d.license_days_left <= 14 && <div className="bg-amber-50 text-amber-600 rounded-xl p-3 mb-4 text-sm">License expires in {d.license_days_left} day(s).</div>}
      {d.active_trip && (
        <div className="bg-gradient-to-br from-brand-600 to-brand-700 text-white rounded-2xl p-6 shadow-lg mb-4">
          <p className="text-sm text-brand-100 mb-1">Active Trip</p>
          <p className="text-xl font-bold">{d.active_trip.source} → {d.active_trip.destination}</p>
        </div>
      )}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 className="font-semibold mb-3">Recent Trips</h3>
        <div className="space-y-2">
          {(d.recent_trips || []).map((t) => (
            <div key={t.id} className="flex justify-between text-sm border-b border-gray-100 dark:border-gray-700 pb-2">
              <span>{t.source} → {t.destination}</span>
              <span className="text-gray-500 capitalize">{t.status}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function SafetyView({ d }) {
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <Card label="Total Drivers" value={d.total_drivers} icon={Users} tint="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" />
        <Card label="On Trip" value={d.on_trip} icon={Route} tint="bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400" />
        <Card label="Suspended" value={d.suspended} icon={ShieldAlert} tint="bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400" />
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="font-semibold mb-3">Expiring / Expired Licenses</h3>
          {[...d.expired_licenses, ...d.expiring_soon].length === 0 && <p className="text-sm text-gray-500">None — all clear.</p>}
          {d.expired_licenses.map((x) => <div key={x.id} className="text-sm text-red-600 border-b border-gray-100 dark:border-gray-700 py-1.5">{x.name} — expired</div>)}
          {d.expiring_soon.map((x) => <div key={x.id} className="text-sm text-amber-600 border-b border-gray-100 dark:border-gray-700 py-1.5">{x.name} — {x.days_left}d left</div>)}
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
          <h3 className="font-semibold mb-3">Low Safety Scores</h3>
          {d.low_safety_scores.map((x) => <div key={x.id} className="flex justify-between text-sm border-b border-gray-100 dark:border-gray-700 py-1.5"><span>{x.name}</span><span className="text-red-600">{x.safety_score}</span></div>)}
        </div>
      </div>
    </>
  );
}

function FinanceView({ d }) {
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <Card label="Total Revenue" value={`₹${d.total_revenue}`} icon={IndianRupee} tint="bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400" />
        <Card label="Operational Cost" value={`₹${d.operational_cost}`} icon={Wrench} tint="bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400" />
        <Card label="Net Margin" value={`₹${d.net_margin}`} icon={Gauge} tint="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" />
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 className="font-semibold mb-3">ROI Leaderboard</h3>
        <div className="space-y-2">
          {d.roi_leaderboard.map((v) => (
            <div key={v.vehicle_id} className="flex justify-between text-sm border-b border-gray-100 dark:border-gray-700 pb-2">
              <span>{v.registration_number}</span>
              <span className="text-gray-500">ROI {v.roi}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

const VIEWS = { fleet_manager: FleetManagerView, driver: DriverView, safety_officer: SafetyView, financial_analyst: FinanceView };

export default function Dashboard() {
  const [payload, setPayload] = useState(null);

  useEffect(() => {
    api.get("/analytics/dashboard/me").then((res) => setPayload(res.data));
  }, []);

  if (!payload) return <div className="text-gray-500">Loading dashboard…</div>;

  const View = VIEWS[payload.role] || FleetManagerView;

  return (
    <div>
      <h1 className="text-2xl font-display font-bold mb-1">Operations Dashboard</h1>
      <p className="text-sm text-gray-500 mb-6 capitalize">{payload.role?.replace("_", " ")} view — real-time snapshot</p>
      <View d={payload.data} />
    </div>
  );
}
