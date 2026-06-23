<template>
  <div class="app">
    <nav class="rail" aria-label="Основная навигация">
      <router-link to="/" aria-label="Лента">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 12.5 12 5l8 7.5V20a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-7.5Z" />
        </svg>
        <span>Лента</span>
      </router-link>
      <router-link to="/create" aria-label="Создать">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 5v14M5 12h14" />
        </svg>
        <span>Создать</span>
      </router-link>
      <router-link to="/history" aria-label="Профиль">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 9a7 7 0 0 0-14 0" />
        </svg>
        <span>Профиль</span>
      </router-link>
    </nav>
    <main class="shell">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useUserStore } from "./stores/user";

const userStore = useUserStore();
userStore.load();
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: var(--surface-muted);
  color: var(--text-main);
}
.shell {
  min-height: 100vh;
  padding-left: 72px;
}
.rail {
  position: fixed;
  z-index: 40;
  top: 50%;
  left: 12px;
  display: grid;
  gap: 10px;
  width: 50px;
  padding: 8px 6px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 26px;
  background: rgba(10, 10, 10, 0.92);
  box-shadow: var(--shadow-floating);
  transform: translateY(-50%);
  backdrop-filter: blur(18px);
}
.rail a {
  position: relative;
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 19px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.58);
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}
.rail a.router-link-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
  transform: scale(1.04);
}
.rail svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.rail a:first-child svg {
  fill: currentColor;
  stroke-width: 1.5;
}
.rail span {
  position: absolute;
  left: 48px;
  padding: 6px 9px;
  border-radius: 12px;
  color: #fff;
  background: #111;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transform: translateX(-4px);
  transition: opacity 0.16s ease, transform 0.16s ease;
}
.rail a:hover span,
.rail a:focus-visible span {
  opacity: 1;
  transform: translateX(0);
}

:global(*) {
  box-sizing: border-box;
}
:global(:root) {
  --surface-main: #ffffff;
  --surface-muted: #f4f4f2;
  --surface-soft: #ededeb;
  --text-main: #111111;
  --text-muted: #6f6f6b;
  --text-faint: #9a9a95;
  --line-soft: #deded9;
  --line-strong: #cfcfca;
  --black: #111111;
  --radius-card: 28px;
  --shadow-floating: 0 24px 70px rgba(17, 17, 17, 0.14);
  --shadow-soft: 0 14px 42px rgba(17, 17, 17, 0.09);
}
:global(html),
:global(body),
:global(#app) {
  min-height: 100%;
  margin: 0;
}
:global(body) {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--surface-muted);
  color: var(--text-main);
}
:global(button),
:global(input),
:global(select) {
  font: inherit;
}

@media (max-width: 430px) {
  .shell {
    padding-left: 56px;
  }
  .rail {
    left: 6px;
    width: 44px;
    padding: 7px 4px;
  }
  .rail a {
    width: 34px;
    height: 34px;
  }
  .rail span {
    display: none;
  }
}
</style>
