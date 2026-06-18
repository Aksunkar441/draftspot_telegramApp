import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
});

// Подпись Telegram WebApp.initData отправляется в каждом запросе —
// FastAPI проверяет её на сервере (см. app/core/security.py),
// чтобы исключить подмену telegram_id на клиенте.
client.interceptors.request.use((config) => {
  const initData = window.Telegram?.WebApp?.initData ?? "";
  config.headers["X-Telegram-Init-Data"] = initData;
  return config;
});

export default client;
