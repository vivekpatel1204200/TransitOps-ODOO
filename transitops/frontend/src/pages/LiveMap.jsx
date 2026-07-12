import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";

// fix default marker icon paths for Vite bundling
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const truckIcon = new L.DivIcon({
  html: "🚚",
  className: "text-2xl",
  iconSize: [30, 30],
});

export default function LiveMap() {
  const [trips, setTrips] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/tracking");
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTrips(data.trips || []);
    };
    return () => ws.close();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Live Trip Tracking</h1>
      <p className="text-sm text-gray-500 mb-4">{trips.length} active trip(s) on the road — updates every 2s via WebSocket</p>
      <div className="rounded-xl overflow-hidden shadow" style={{ height: "600px" }}>
        <MapContainer center={[22.5, 71.5]} zoom={7} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {trips.map((t) => (
            <Marker key={t.trip_id} position={[t.lat, t.lng]} icon={truckIcon}>
              <Popup>
                <b>{t.source} → {t.destination}</b><br />
                Vehicle: {t.vehicle_id.slice(0, 8)}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
