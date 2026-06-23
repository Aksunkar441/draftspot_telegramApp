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
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { getMyEvents, deleteEvent } from "../../api/events";

const events = ref([]);
const loading = ref(false);
const actionLoading = ref(false);
const error = ref("");
const router = useRouter();
const emit = defineEmits(["count"]);

watch(events, (items) => emit("count", items.length), { immediate: true });

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
  border: 1px solid var(--line-soft);
  border-radius: 20px;
  padding: 14px;
  background: #fff;
  box-shadow: var(--shadow-soft);
  cursor: pointer;
}
.item p {
  margin: 0 0 6px;
}
.item p:first-child {
  font-weight: 800;
}
.item button {
  margin-top: 8px;
  padding: 9px 12px;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: var(--surface-muted);
  color: var(--text-main);
  font-weight: 800;
}
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 32px 16px;
}
.empty button {
  margin-top: 8px;
  padding: 9px 14px;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: #fff;
  color: var(--text-main);
  font-weight: 800;
}
button:disabled {
  opacity: 0.65;
}
</style>
