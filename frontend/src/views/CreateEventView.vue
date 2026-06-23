<template>
  <section class="create-page">
    <header>
      <p>Новая игра</p>
      <h1>Опубликовать сбор</h1>
    </header>

    <form class="create-form" @submit.prevent="submit">
      <label>
        Поле
        <select v-model.number="form.venue_id" :disabled="loadingVenues || !venues.length" required>
          <option v-for="venue in venues" :key="venue.id" :value="venue.id">
            {{ venue.name }} ({{ venue.is_paid ? venue.price + " ₸" : "бесплатно" }})
          </option>
        </select>
      </label>
      <p v-if="loadingVenues" class="hint">Загружаем поля...</p>
      <p v-else-if="venueError" class="error">{{ venueError }}</p>

      <label>
        Вид спорта (необязательно)
        <input v-model="form.sport_type" type="text" placeholder="Футбол, баскетбол, теннис" />
      </label>

      <label>
        Сколько игроков нужно
        <input v-model.number="form.slots_total" type="number" min="1" required />
      </label>

      <label>
        Время проведения (необязательно)
        <input v-model="form.scheduled_at" type="datetime-local" />
      </label>

      <label>
        Ссылка на группу (необязательно)
        <input v-model="form.group_link" type="url" placeholder="https://t.me/..." />
      </label>

      <p v-if="submitError" class="error">{{ submitError }}</p>

      <button type="submit" :disabled="submitting || loadingVenues || !form.venue_id">
        {{ submitting ? "Публикуем..." : "Опубликовать" }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getVenues, createEvent } from "../api/events";

const venues = ref([]);
const loadingVenues = ref(false);
const venueError = ref("");
const submitError = ref("");
const submitting = ref(false);
const router = useRouter();

const form = reactive({
  venue_id: null,
  sport_type: "",
  slots_total: 2,
  scheduled_at: "",
  group_link: "",
});

onMounted(async () => {
  loadingVenues.value = true;
  venueError.value = "";
  try {
    venues.value = await getVenues();
    if (venues.value.length && !form.venue_id) {
      form.venue_id = venues.value[0].id;
    }
  } catch (error) {
    venueError.value = "Не удалось загрузить список полей";
  } finally {
    loadingVenues.value = false;
  }
});

async function submit() {
  submitError.value = "";
  const selectedVenue = venues.value.find((v) => v.id === form.venue_id);
  const payload = {
    ...form,
    price: selectedVenue?.is_paid ? selectedVenue.price : null,
    scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : null,
  };
  submitting.value = true;
  try {
    const event = await createEvent(payload);
    router.push({ name: "event-detail", params: { id: event.id } });
  } catch (error) {
    submitError.value = error.response?.data?.detail ?? "Не удалось опубликовать событие";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.create-page {
  min-height: 100svh;
  padding: 24px min(5vw, 28px);
  background:
    linear-gradient(90deg, rgba(17, 17, 17, 0.035) 1px, transparent 1px),
    linear-gradient(0deg, rgba(17, 17, 17, 0.035) 1px, transparent 1px),
    var(--surface-muted);
  background-size: 48px 48px;
}
.create-page header {
  max-width: 560px;
  margin: 0 auto 18px;
}
.create-page header p {
  margin: 0 0 6px;
  color: var(--text-faint);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.create-page header h1 {
  margin: 0;
  color: var(--text-main);
  font-size: clamp(30px, 8vw, 44px);
  line-height: 0.98;
}
.create-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 560px;
  margin: 0 auto;
  padding: 18px;
  border: 1px solid var(--line-soft);
  border-radius: 24px;
  background: #fff;
  box-shadow: var(--shadow-floating);
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 800;
  color: var(--text-muted);
}
input,
select {
  min-height: 48px;
  padding: 0 13px;
  border: 1px solid var(--line-soft);
  border-radius: 14px;
  background: var(--surface-muted);
  color: var(--text-main);
  outline: none;
}
input:focus,
select:focus {
  border-color: var(--black);
  box-shadow: 0 0 0 3px rgba(17, 17, 17, 0.08);
}
button[type="submit"] {
  min-height: 52px;
  border: none;
  border-radius: 999px;
  background: var(--black);
  color: #fff;
  font-weight: 950;
}
button:disabled,
select:disabled {
  opacity: 0.65;
}
.hint,
.error {
  margin: -8px 0 0;
  font-size: 13px;
}
.hint {
  color: var(--text-muted);
}
.error {
  color: var(--text-main);
}

@media (max-width: 430px) {
  .create-page {
    padding: 18px 10px;
  }
  .create-form {
    padding: 14px;
    border-radius: 20px;
  }
}
</style>
