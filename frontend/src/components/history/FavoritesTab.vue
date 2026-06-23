<template>
  <div class="list">
    <p v-if="loading" class="empty">Загружаем избранное...</p>
    <div v-else-if="error" class="empty">
      <p>{{ error }}</p>
      <button @click="load">Повторить</button>
    </div>

    <article
      v-for="favorite in favorites"
      :key="favorite.id"
      class="item"
      :class="{ unavailable: !favorite.is_available }"
      @click="open(favorite)"
    >
      <div class="item-main">
        <p>{{ favorite.event.venue.name }} — {{ favorite.event.sport_type || "без вида спорта" }}</p>
        <p v-if="favorite.event.scheduled_at">
          {{ new Date(favorite.event.scheduled_at).toLocaleString("ru-RU") }}
        </p>
        <p>{{ favorite.event.slots_available }} / {{ favorite.event.slots_total }} мест</p>
      </div>

      <p v-if="!favorite.is_available" class="reason">
        {{ favorite.unavailable_reason || "Игра больше недоступна" }}
      </p>

      <button :disabled="actionLoading" @click.stop="remove(favorite)">Убрать</button>
    </article>

    <p v-if="!loading && !error && !favorites.length" class="empty">Избранных игр пока нет</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { getFavorites, removeFavorite } from "../../api/favorites";
import { DEMO_EVENTS, isLocalDemoMode } from "../../stores/events";

const favorites = ref([]);
const loading = ref(false);
const actionLoading = ref(false);
const error = ref("");
const router = useRouter();
const emit = defineEmits(["count"]);

watch(favorites, (items) => emit("count", items.length), { immediate: true });

function readLocalFavoriteIds() {
  try {
    return JSON.parse(localStorage.getItem("draftspot:saved-events") || "[]");
  } catch {
    return [];
  }
}

function writeLocalFavoriteIds(ids) {
  localStorage.setItem("draftspot:saved-events", JSON.stringify([...new Set(ids)]));
}

function demoFavorites() {
  const ids = readLocalFavoriteIds();
  return DEMO_EVENTS.filter((event) => ids.includes(event.id)).map((event) => ({
    id: event.id,
    event,
    is_available: event.status ? event.status === "open" : true,
    unavailable_reason: event.status === "completed" ? "Игра закончилась" : null,
  }));
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    if (isLocalDemoMode()) {
      favorites.value = demoFavorites();
    } else {
      favorites.value = await getFavorites();
    }
  } catch {
    error.value = "Не удалось загрузить избранное";
  } finally {
    loading.value = false;
  }
}

function open(favorite) {
  if (!favorite.is_available) return;
  router.push({ name: "event-detail", params: { id: favorite.event.id } });
}

async function remove(favorite) {
  actionLoading.value = true;
  error.value = "";
  try {
    if (isLocalDemoMode()) {
      writeLocalFavoriteIds(readLocalFavoriteIds().filter((id) => id !== favorite.event.id));
    } else {
      await removeFavorite(favorite.event.id);
    }
    await load();
  } catch {
    error.value = "Не удалось убрать из избранного";
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
  cursor: pointer;
}
.item.unavailable {
  background: #eeeeeb;
  color: var(--text-muted);
  cursor: default;
  box-shadow: none;
}
.item p {
  margin: 0 0 6px;
}
.item-main p:first-child {
  color: var(--text-main);
  font-weight: 850;
}
.unavailable .item-main p:first-child {
  color: var(--text-muted);
}
.reason {
  display: inline-flex;
  padding: 7px 10px;
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 850;
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
