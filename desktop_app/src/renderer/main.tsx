import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app";
import "./styles/app.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Renderer root element not found");
}

createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
