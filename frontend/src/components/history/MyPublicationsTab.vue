<template>
  <div class="list">
    <div v-for="event in events" :key="event.id" class="item" @click="open(event.id)">
      <p>{{ event.venue.name }} — {{ event.sport_type || "без вида спорта" }}</p>
      <p>Мест: {{ event.slots_available }} / {{ event.slots_total }}</p>
      <p v-if="event.price">Собрано: {{ (event.slots_total - event.slots_available) * event.price }} ₸</p>
      <button @click.stop="remove(event.id)">Удалить</button>
    </div>
    <p v-if="!events.length" class="empty">У вас пока нет публикаций</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMyEvents, deleteEvent } from "../../api/events";

const events = ref([]);
const router = useRouter();

async function load() {
  events.value = await getMyEvents();
}

function open(id) {
  router.push({ name: "event-detail", params: { id } });
}

async function remove(id) {
  await deleteEvent(id);
  await load();
}

onMounted(load);
</script>

<style scoped>
.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 16px;
}
.item {
  border-radius: 12px;
  padding: 14px;
  background: #fff;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
}
.empty {
  text-align: center;
  color: #888;
}
</style>
