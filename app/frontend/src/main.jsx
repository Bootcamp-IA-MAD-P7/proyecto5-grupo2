import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import BetaApp from "./BetaApp.jsx";
import "./styles.css";

const params = new URLSearchParams(window.location.search);
const useBetaApp = params.get("variant") === "beta" || import.meta.env.VITE_APP_VARIANT === "beta";
const RootApp = useBetaApp ? BetaApp : App;

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RootApp />
  </React.StrictMode>
);
