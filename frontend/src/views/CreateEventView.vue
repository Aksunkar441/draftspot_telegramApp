<template>
  <form class="create-form" @submit.prevent="submit">
    <label>
      Поле
      <select v-model="form.venue_id" required>
        <option v-for="venue in venues" :key="venue.id" :value="venue.id">
          {{ venue.name }} ({{ venue.is_paid ? venue.price + " ₸" : "бесплатно" }})
        </option>
      </select>
    </label>

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

    <button type="submit">Опубликовать</button>
  </form>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getVenues, createEvent } from "../api/events";

const venues = ref([]);
const router = useRouter();

const form = reactive({
  venue_id: null,
  sport_type: "",
  slots_total: 2,
  scheduled_at: "",
  group_link: "",
});

onMounted(async () => {
  venues.value = await getVenues();
});

async function submit() {
  const selectedVenue = venues.value.find((v) => v.id === form.venue_id);
  const payload = {
    ...form,
    price: selectedVenue?.is_paid ? selectedVenue.price : null,
    scheduled_at: form.scheduled_at ? new Date(form.scheduled_at).toISOString() : null,
  };
  const event = await createEvent(payload);
  router.push({ name: "event-detail", params: { id: event.id } });
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
</style>
