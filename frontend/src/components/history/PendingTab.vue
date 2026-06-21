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
import { ref, onMounted } from "vue";
import { getPending, cancelApplication } from "../../api/applications";

const applications = ref([]);
const loading = ref(false);
const actionLoading = ref(false);
const error = ref("");

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
  border-radius: 12px;
  padding: 14px;
  background: #fff;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
}
.status {
  color: #f5a623;
  font-size: 13px;
}
.empty {
  text-align: center;
  color: #888;
}
button:disabled {
  opacity: 0.65;
}
</style>
