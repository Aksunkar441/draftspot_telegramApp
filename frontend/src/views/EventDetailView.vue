<template>
  <section v-if="event" class="detail">
    <header class="detail-hero">
      <p>{{ event.venue.city || "Тараз" }}</p>
      <h1>{{ event.sport_type || event.venue.sport_type || "Игра" }}</h1>
      <span>{{ event.venue.name }} — {{ event.venue.address || "адрес уточняется" }}</span>
    </header>

    <div class="summary">
      <div>
        <span>Когда</span>
        <strong>{{ event.scheduled_at ? new Date(event.scheduled_at).toLocaleString("ru-RU") : "Время уточняется" }}</strong>
      </div>
      <div>
        <span>Цена</span>
        <strong>{{ event.price ? event.price + " ₸" : "Бесплатно" }}</strong>
      </div>
      <div>
        <span>Мест</span>
        <strong>{{ event.slots_available }} / {{ event.slots_total }}</strong>
      </div>
    </div>

    <a v-if="event.group_link" class="group-link" :href="event.group_link" target="_blank" rel="noreferrer">
      Открыть группу
    </a>

    <div v-if="!isCaptain" class="player-actions">
      <button
        v-if="canJoin"
        class="join-action"
        :disabled="actionLoading"
        @click="join"
      >
        {{ actionLoading ? "Отправляем..." : "Записаться на игру" }}
      </button>
      <p v-else class="unavailable-note">{{ unavailableReason }}</p>
      <p v-if="actionMessage" class="action-message">{{ actionMessage }}</p>
    </div>

    <VenueMapPreview :venue="event.venue" />

    <div v-if="isCaptain" class="applicants">
      <h3>Заявки</h3>
      <div v-for="app in event.applicants" :key="app.id" class="applicant">
        <span>{{ app.user_name }} — {{ statusLabel(app.status) }}</span>
        <div v-if="app.status === 'pending'" class="buttons">
          <button :disabled="actionLoading" @click="accept(app.id)">Принять</button>
          <button :disabled="actionLoading" @click="decline(app.id)">Отклонить</button>
        </div>
        <button v-else-if="app.status === 'accepted'" :disabled="actionLoading" @click="kick(app.id)">Исключить</button>
      </div>
      <p v-if="!event.applicants.length" class="empty">Заявок пока нет</p>
    </div>
  </section>
  <p v-else-if="loading" class="empty">Загружаем событие...</p>
  <div v-else class="empty">
    <p>{{ error || "Событие не найдено" }}</p>
    <button @click="load">Повторить</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { getEvent, joinEvent } from "../api/events";
import { acceptApplication, declineApplication, kickPlayer } from "../api/applications";
import { useUserStore } from "../stores/user";
import VenueMapPreview from "../components/VenueMapPreview.vue";

const props = defineProps({ id: { type: [String, Number], required: true } });
const event = ref(null);
const loading = ref(false);
const actionLoading = ref(false);
const actionMessage = ref("");
const error = ref("");
const userStore = useUserStore();

const isCaptain = computed(
  () => event.value && userStore.profile && event.value.captain_id === userStore.profile.id
);

const canJoin = computed(
  () => event.value?.status === "open" && Number(event.value?.slots_available) > 0
);

const unavailableReason = computed(() => {
  if (!event.value) return "";
  if (event.value.status === "completed") return "Игра уже закончилась";
  if (event.value.status === "cancelled") return "Игра отменена";
  if (event.value.status === "full" || Number(event.value.slots_available) <= 0) return "Мест больше нет";
  return "Сейчас нельзя подать заявку";
});

function statusLabel(status) {
  return { pending: "ожидает ответа", accepted: "принят", declined: "отклонён", cancelled: "отменён" }[status] ?? status;
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    event.value = await getEvent(props.id);
  } catch {
    event.value = null;
    error.value = "Не удалось открыть событие";
  } finally {
    loading.value = false;
  }
}

async function accept(appId) {
  await runAction(() => acceptApplication(appId));
}
async function decline(appId) {
  await runAction(() => declineApplication(appId));
}
async function kick(appId) {
  await runAction(() => kickPlayer(appId));
}

async function join() {
  actionLoading.value = true;
  actionMessage.value = "";
  error.value = "";
  try {
    await joinEvent(event.value.id);
    actionMessage.value = "Заявка отправлена капитану";
    await load();
  } catch (e) {
    actionMessage.value = e.response?.data?.detail ?? "Не удалось отправить заявку";
  } finally {
    actionLoading.value = false;
  }
}

async function runAction(action) {
  actionLoading.value = true;
  error.value = "";
  try {
    await action();
    await load();
  } catch (e) {
    error.value = e.response?.data?.detail ?? "Не удалось выполнить действие";
  } finally {
    actionLoading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.detail {
  min-height: 100svh;
  padding: 24px min(5vw, 28px);
  background:
    linear-gradient(90deg, rgba(17, 17, 17, 0.035) 1px, transparent 1px),
    linear-gradient(0deg, rgba(17, 17, 17, 0.035) 1px, transparent 1px),
    var(--surface-muted);
  background-size: 48px 48px;
  color: var(--text-main);
}
.detail-hero {
  max-width: 760px;
  margin: 0 auto 16px;
}
.detail-hero p {
  margin: 0 0 6px;
  color: var(--text-faint);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.detail-hero h1 {
  margin: 0;
  font-size: clamp(34px, 9vw, 62px);
  line-height: 0.94;
}
.detail-hero span {
  display: block;
  margin-top: 12px;
  color: var(--text-muted);
  line-height: 1.35;
}
.summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  max-width: 760px;
  margin: 0 auto 14px;
}
.summary div {
  min-width: 0;
  padding: 14px;
  border: 1px solid var(--line-soft);
  border-radius: 18px;
  background: #fff;
  box-shadow: var(--shadow-soft);
}
.summary span,
.summary strong {
  display: block;
}
.summary span {
  margin-bottom: 6px;
  color: var(--text-faint);
  font-size: 11px;
  font-weight: 900;
}
.summary strong {
  overflow-wrap: anywhere;
  font-size: 14px;
}
.group-link {
  display: block;
  max-width: 760px;
  margin: 0 auto 16px;
  padding: 14px;
  border-radius: 999px;
  background: var(--black);
  color: #fff;
  font-weight: 950;
  text-align: center;
  text-decoration: none;
}
.player-actions {
  max-width: 760px;
  margin: 0 auto 16px;
}
.join-action {
  width: 100%;
  min-height: 52px;
  border-radius: 999px;
  border-color: var(--black);
  background: var(--black);
  color: #fff;
  font-weight: 950;
}
.unavailable-note,
.action-message {
  margin: 0;
  padding: 12px 14px;
  border: 1px solid var(--line-soft);
  border-radius: 18px;
  background: #fff;
  color: var(--text-muted);
  text-align: center;
  box-shadow: var(--shadow-soft);
}
.action-message {
  margin-top: 8px;
  color: var(--text-main);
}
.detail :deep(.map-card) {
  max-width: 760px;
  margin: 0 auto 18px;
}
.applicants {
  max-width: 760px;
  margin-top: 24px;
  margin-right: auto;
  margin-left: auto;
  padding: 16px;
  border: 1px solid var(--line-soft);
  border-radius: 22px;
  background: #fff;
  box-shadow: var(--shadow-soft);
}
.applicants h3 {
  margin: 0 0 10px;
}
.applicant {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--line-soft);
  gap: 12px;
}
.buttons {
  display: flex;
  gap: 8px;
}
.empty {
  color: var(--text-muted);
  padding: 16px;
  text-align: center;
}
button {
  padding: 8px 10px;
  border: 0;
  border-radius: 9px;
  border: 1px solid var(--line-soft);
  background: var(--surface-muted);
  color: var(--text-main);
  font-weight: 850;
}
button:disabled {
  opacity: 0.65;
}

@media (max-width: 430px) {
  .detail {
    padding: 18px 10px;
  }
  .summary {
    grid-template-columns: 1fr;
  }
  .applicant {
    align-items: start;
    flex-direction: column;
  }
}
</style>
