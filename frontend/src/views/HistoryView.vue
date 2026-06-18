<template>
  <div class="history">
    <div class="tabs">
      <button :class="{ active: tab === 'my' }" @click="tab = 'my'">Мои публикации</button>
      <button :class="{ active: tab === 'pending' }" @click="tab = 'pending'">Ожидание</button>
      <button :class="{ active: tab === 'upcoming' }" @click="tab = 'upcoming'">Предстоящие</button>
    </div>

    <MyPublicationsTab v-if="tab === 'my'" />
    <PendingTab v-else-if="tab === 'pending'" />
    <UpcomingTab v-else />
  </div>
</template>

<script setup>
import { ref } from "vue";
import MyPublicationsTab from "../components/history/MyPublicationsTab.vue";
import PendingTab from "../components/history/PendingTab.vue";
import UpcomingTab from "../components/history/UpcomingTab.vue";

const tab = ref("my");
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 8px;
  padding: 16px;
}
.tabs button {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  border: none;
  background: #f0f0f0;
  font-weight: 500;
}
.tabs button.active {
  background: var(--tg-theme-button-color, #2ea6ff);
  color: #fff;
}
</style>
