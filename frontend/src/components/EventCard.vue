<template>
  <div class="card">
    <h3>{{ event.sport_type || "Игра без названия" }}</h3>
    <p class="venue">{{ event.venue.name }}</p>
    <p v-if="event.scheduled_at">{{ formattedTime }}</p>
    <p v-if="event.price">Цена: {{ event.price }} ₸</p>
    <p>Свободно мест: {{ event.slots_available }} / {{ event.slots_total }}</p>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({ event: { type: Object, required: true } });

const formattedTime = computed(() => new Date(props.event.scheduled_at).toLocaleString("ru-RU"));
</script>

<style scoped>
.card {
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  background: #fff;
}
.venue {
  color: #666;
}
</style>
