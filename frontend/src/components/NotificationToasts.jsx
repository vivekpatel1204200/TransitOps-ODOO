import { useEffect, useRef, useState } from "react";
import { Bell, X } from "lucide-react";
import { WS_URL } from "../api/client";

export default function NotificationToasts() {
  const [toasts, setToasts] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const connect = () => {
      const ws = new WebSocket(`${WS_URL}/ws/events?token=${token}`);
      wsRef.current = ws;
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === "connected") return;
          const id = Date.now() + Math.random();
          setToasts((t) => [...t, { id, ...data }].slice(-4));
          setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 6000);
        } catch { /* ignore malformed payloads */ }
      };
      ws.onclose = () => setTimeout(connect, 3000);
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  const tint = (sev) => ({
    critical: "bg-red-50 border-red-200 text-red-700",
    warning: "bg-amber-50 border-amber-200 text-amber-700",
    info: "bg-blue-50 border-blue-200 text-blue-700",
  }[sev] || "bg-gray-50 border-gray-200 text-gray-700");

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 w-80">
      {toasts.map((t) => (
        <div key={t.id} className={`flex items-start gap-2 border rounded-xl p-3 shadow-lg ${tint(t.severity)}`}>
          <Bell size={16} className="mt-0.5 shrink-0" />
          <div className="flex-1 text-sm">
            <p className="font-semibold">{t.title}</p>
            <p className="opacity-80">{t.message}</p>
          </div>
          <button onClick={() => setToasts((ts) => ts.filter((x) => x.id !== t.id))}><X size={14} /></button>
        </div>
      ))}
    </div>
  );
}
