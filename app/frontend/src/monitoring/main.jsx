import React from "react";
import { createRoot } from "react-dom/client";
import MonitoringDashboard from "./MonitoringDashboard.jsx";
import "./monitoring.css";

createRoot(document.getElementById("monitoring-root")).render(
  <React.StrictMode>
    <MonitoringDashboard />
  </React.StrictMode>
);
