<template>
  <div class="feed">
    <EventCard v-if="store.current" :event="store.current" @click="openDetail" />
    <p v-else class="empty">Новых публикаций пока нет</p>

    <div class="actions" v-if="store.current">
      <button class="skip" @click="store.skip">Смотреть дальше</button>
      <button class="join" @click="handleJoin">Присоединиться</button>
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

onMounted(() => store.loadFeed());

function openDetail() {
  if (store.current) router.push({ name: "event-detail", params: { id: store.current.id } });
}

async function handleJoin() {
  await store.join();
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
.skip {
  background: #f0f0f0;
}
.join {
  background: var(--tg-theme-button-color, #2ea6ff);
  color: var(--tg-theme-button-text-color, #fff);
}
</style>
