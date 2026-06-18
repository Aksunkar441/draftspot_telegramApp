<template>
  <div class="app">
    <router-view />
    <nav class="tabbar">
      <router-link to="/">Лента</router-link>
      <router-link to="/create">Создать</router-link>
      <router-link to="/history">История</router-link>
    </nav>
  </div>
</template>

<script setup>
import { useUserStore } from "./stores/user";

const userStore = useUserStore();
userStore.load();
</script>

<style scoped>
.app {
  padding-bottom: 56px;
}
.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  background: var(--tg-theme-bg-color, #fff);
  border-top: 1px solid #e5e5e5;
}
.tabbar a {
  text-decoration: none;
  color: var(--tg-theme-text-color, #222);
  font-weight: 600;
}
.tabbar a.router-link-active {
  color: var(--tg-theme-button-color, #2ea6ff);
}
</style>
