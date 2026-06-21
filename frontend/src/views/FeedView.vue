<template>
  <div class="feed">
    <EventCard v-if="store.current" :event="store.current" @click="openDetail" />
    <p v-else-if="store.loading" class="empty">Загружаем публикации...</p>
    <div v-else-if="store.error" class="empty">
      <p>Не удалось загрузить ленту</p>
      <button @click="reload">Повторить</button>
    </div>
    <p v-else class="empty">Новых публикаций пока нет</p>

    <p v-if="store.actionError" class="error">{{ store.actionError }}</p>

    <div class="actions" v-if="store.current">
      <button class="skip" :disabled="store.actionLoading" @click="handleSkip">Смотреть дальше</button>
      <button class="join" :disabled="store.actionLoading" @click="handleJoin">
        {{ store.actionLoading ? "Отправляем..." : "Присоединиться" }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import EventCard from "../components/EventCard.vue";
import { useEventsStore } from "../stores/events";

const store = useEventsStore();
const router = useRouter();

onMounted(() => store.loadFeed({ reset: true }));

function reload() {
  store.loadFeed({ reset: true });
}

function openDetail() {
  if (store.current) router.push({ name: "event-detail", params: { id: store.current.id } });
}

async function handleJoin() {
  await store.join();
}

async function handleSkip() {
  await store.skip();
}
</script>

<style scoped>
.feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}
.empty {
  text-align: center;
  color: #888;
  margin-top: 40px;
}
.actions {
  display: flex;
  gap: 12px;
}
.actions button {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
}
.actions button:disabled {
  opacity: 0.65;
}
.error {
  color: #d64545;
  font-size: 13px;
  text-align: center;
}
.skip {
  background: #f0f0f0;
}
.join {
  background: var(--tg-theme-button-color, #2ea6ff);
  color: var(--tg-theme-button-text-color, #fff);
}
</style>
