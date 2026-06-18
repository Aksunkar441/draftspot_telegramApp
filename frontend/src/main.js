import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

createApp(App).use(createPinia()).use(router).mount("#app");
