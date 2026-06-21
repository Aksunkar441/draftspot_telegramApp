<template>
  <div class="list">
    <p v-if="loading" class="empty">Загружаем публикации...</p>
    <div v-else-if="error" class="empty">
      <p>{{ error }}</p>
      <button @click="load">Повторить</button>
    </div>
    <div v-for="event in events" :key="event.id" class="item" @click="open(event.id)">
      <p>{{ event.venue.name }} — {{ event.sport_type || "без вида спорта" }}</p>
      <p>Мест: {{ event.slots_available }} / {{ event.slots_total }}</p>
      <p v-if="event.price">Собрано: {{ (event.slots_total - event.slots_available) * event.price }} ₸</p>
      <button :disabled="actionLoading" @click.stop="remove(event.id)">Удалить</button>
    </div>
    <p v-if="!loading && !error && !events.length" class="empty">У вас пока нет публикаций</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMyEvents, deleteEvent } from "../../api/events";

const events = ref([]);
const loading = ref(false);
const actionLoading = ref(false);
const error = ref("");
const router = useRouter();

async function load() {
  loading.value = true;
  error.value = "";
  try {
    events.value = await getMyEvents();
  } catch {
    error.value = "Не удалось загрузить публикации";
  } finally {
    loading.value = false;
  }
}

function open(id) {
  router.push({ name: "event-detail", params: { id } });
}

async function remove(id) {
  actionLoading.value = true;
  error.value = "";
  try {
    await deleteEvent(id);
    await load();
  } catch {
    error.value = "Не удалось удалить публикацию";
  } finally {
    actionLoading.value = false;
  }
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
button:disabled {
  opacity: 0.65;
}
</style>
