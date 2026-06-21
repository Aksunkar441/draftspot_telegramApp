<template>
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
      <input v-model="form.sport_type" type="text" />
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
      <input v-model="form.group_link" type="url" />
    </label>

    <p v-if="submitError" class="error">{{ submitError }}</p>

    <button type="submit" :disabled="submitting || loadingVenues || !form.venue_id">
      {{ submitting ? "Публикуем..." : "Опубликовать" }}
    </button>
  </form>
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
.create-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  color: #555;
}
input,
select {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
}
button[type="submit"] {
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  background: var(--tg-theme-button-color, #2ea6ff);
  color: var(--tg-theme-button-text-color, #fff);
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
  color: #777;
}
.error {
  color: #d64545;
}
</style>
