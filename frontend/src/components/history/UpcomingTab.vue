<template>
  <div class="list">
    <div v-for="app in applications" :key="app.id" class="item">
      <p>{{ app.event.venue.name }} — {{ app.event.sport_type || "без вида спорта" }}</p>
      <p v-if="app.event.scheduled_at">{{ new Date(app.event.scheduled_at).toLocaleString("ru-RU") }}</p>
      <button @click="cancel(app.id)">Отменить</button>
    </div>
    <p v-if="!applications.length" class="empty">Нет предстоящих игр</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getUpcoming, cancelApplication } from "../../api/applications";

const applications = ref([]);

async function load() {
  applications.value = await getUpcoming();
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
.empty {
  text-align: center;
  color: #888;
}
</style>
