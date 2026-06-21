import axios from "axios";

const apiBaseURL = import.meta.env.VITE_API_BASE_URL ?? "/api";

const client = axios.create({
  baseURL: apiBaseURL,
});

// Подпись Telegram WebApp.initData отправляется в каждом запросе —
// FastAPI проверяет её на сервере (см. app/core/security.py),
// чтобы исключить подмену telegram_id на клиенте.
client.interceptors.request.use((config) => {
  const initData = window.Telegram?.WebApp?.initData ?? "";
  config.headers["X-Telegram-Init-Data"] = initData;
  if (apiBaseURL.includes("ngrok-free.")) {
    config.headers["ngrok-skip-browser-warning"] = "true";
  }
  return config;
});

export default client;
