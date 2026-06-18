<template>
  <div class="list">
    <div v-for="app in applications" :key="app.id" class="item">
      <p>{{ app.event.venue.name }} — {{ app.event.sport_type || "без вида спорта" }}</p>
      <p v-if="app.event.price">Цена: {{ app.event.price }} ₸</p>
      <p class="status">Ожидание ответа капитана</p>
      <button @click="cancel(app.id)">Отменить</button>
    </div>
    <p v-if="!applications.length" class="empty">Нет ожидающих заявок</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getPending, cancelApplication } from "../../api/applications";

const applications = ref([]);

async function load() {
  applications.value = await getPending();
}

async function cancel(id) {
  await cancelApplication(id);
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
}
.status {
  color: #f5a623;
  font-size: 13px;
}
.empty {
  text-align: center;
  color: #888;
}
</style>
