<template>
  <div class="list">
    <p v-if="loading" class="empty">Загружаем заявки...</p>
    <div v-else-if="error" class="empty">
      <p>{{ error }}</p>
      <button @click="load">Повторить</button>
    </div>
    <div v-for="app in applications" :key="app.id" class="item">
      <p>{{ app.event.venue.name }} — {{ app.event.sport_type || "без вида спорта" }}</p>
      <p v-if="app.event.price">Цена: {{ app.event.price }} ₸</p>
      <p class="status">Ожидание ответа капитана</p>
      <button :disabled="actionLoading" @click="cancel(app.id)">Отменить</button>
    </div>
    <p v-if="!loading && !error && !applications.length" class="empty">Нет ожидающих заявок</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { getPending, cancelApplication } from "../../api/applications";

const applications = ref([]);
const loading = ref(false);
const actionLoading = ref(false);
const error = ref("");
const emit = defineEmits(["count"]);

watch(applications, (items) => emit("count", items.length), { immediate: true });

async function load() {
  loading.value = true;
  error.value = "";
  try {
    applications.value = await getPending();
  } catch {
    error.value = "Не удалось загрузить заявки";
  } finally {
    loading.value = false;
  }
}

async function cancel(id) {
  actionLoading.value = true;
  error.value = "";
  try {
    await cancelApplication(id);
    await load();
  } catch {
    error.value = "Не удалось отменить заявку";
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
.status {
  color: var(--text-muted);
  font-size: 13px;
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
