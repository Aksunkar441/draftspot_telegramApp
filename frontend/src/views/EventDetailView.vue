<template>
  <div v-if="event" class="detail">
    <h2>{{ event.sport_type || "Игра" }}</h2>
    <p>{{ event.venue.name }} — {{ event.venue.address }}</p>
    <p v-if="event.scheduled_at">{{ new Date(event.scheduled_at).toLocaleString("ru-RU") }}</p>
    <p v-if="event.price">Цена: {{ event.price }} ₸</p>
    <p>Мест: {{ event.slots_available }} / {{ event.slots_total }}</p>
    <a v-if="event.group_link" :href="event.group_link" target="_blank">Ссылка на группу</a>

    <div v-if="isCaptain" class="applicants">
      <h3>Заявки</h3>
      <div v-for="app in event.applicants" :key="app.id" class="applicant">
        <span>{{ app.user_name }} — {{ statusLabel(app.status) }}</span>
        <div v-if="app.status === 'pending'" class="buttons">
          <button @click="accept(app.id)">Принять</button>
          <button @click="decline(app.id)">Отклонить</button>
        </div>
        <button v-else-if="app.status === 'accepted'" @click="kick(app.id)">Исключить</button>
      </div>
      <p v-if="!event.applicants.length" class="empty">Заявок пока нет</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { getEvent } from "../api/events";
import { acceptApplication, declineApplication, kickPlayer } from "../api/applications";
import { useUserStore } from "../stores/user";

const props = defineProps({ id: { type: [String, Number], required: true } });
const event = ref(null);
const userStore = useUserStore();

const isCaptain = computed(
  () => event.value && userStore.profile && event.value.captain_id === userStore.profile.id
);

function statusLabel(status) {
  return { pending: "ожидает ответа", accepted: "принят", declined: "отклонён", cancelled: "отменён" }[status] ?? status;
}

async function load() {
  event.value = await getEvent(props.id);
}

async function accept(appId) {
  await acceptApplication(appId);
  await load();
}
async function decline(appId) {
  await declineApplication(appId);
  await load();
}
async function kick(appId) {
  await kickPlayer(appId);
  await load();
}

onMounted(load);
</script>

<style scoped>
.detail {
  padding: 16px;
}
.applicants {
  margin-top: 24px;
}
.applicant {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}
.buttons {
  display: flex;
  gap: 8px;
}
.empty {
  color: #888;
}
</style>
