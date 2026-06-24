<template>
  <section class="feed-screen">
    <button class="close-button" type="button" aria-label="Закрыть" @click="closeApp">
      <span></span>
      <span></span>
    </button>

    <header class="feed-header">
      <p>Draft Spot</p>
      <h1>Найди игру рядом</h1>
    </header>

    <div v-if="store.current" class="deck" :class="{ dragging }">
      <article
        class="event-panel ghost ghost-back"
        :style="ghostBackStyle"
        aria-hidden="true"
      ></article>
      <article
        class="event-panel ghost ghost-front"
        :style="ghostFrontStyle"
        aria-hidden="true"
      ></article>

      <article
        class="event-panel active-card"
        :style="cardStyle"
        @pointerdown="startDrag"
        @pointermove="moveDrag"
        @pointerup="endDrag"
        @pointercancel="cancelDrag"
      >
        <div class="top-row">
          <div class="segmented" role="tablist" aria-label="Режим карточки" @pointerdown.stop>
            <button :class="{ active: mode === 'info' }" type="button" @click.stop="mode = 'info'">
              Игра
            </button>
            <button :class="{ active: mode === 'map' }" type="button" @click.stop="mode = 'map'">
              Карта
            </button>
          </div>
          <span class="slots">{{ store.current.slots_available }}/{{ store.current.slots_total }}</span>
        </div>

        <div v-if="mode === 'info'" class="info-layout">
          <div class="venue-image">
            <span class="image-tag">{{ store.current.venue.city || "Тараз" }}</span>
            <span class="image-number">{{ cardNumber }}</span>
          </div>
          <div class="info-content">
            <p class="sport">{{ store.current.sport_type || store.current.venue.sport_type || "Спорт" }}</p>
            <h2>{{ store.current.venue.name }}</h2>
            <p class="address">{{ store.current.venue.address || "Адрес уточняется" }}</p>

            <div class="metrics">
              <div>
                <span>Когда</span>
                <strong>{{ formattedTime }}</strong>
              </div>
              <div>
                <span>Цена</span>
                <strong>{{ priceLabel }}</strong>
              </div>
              <div>
                <span>Места</span>
                <strong>{{ store.current.slots_available }} свободно</strong>
              </div>
            </div>
          </div>
        </div>

        <VenueMapPreview v-else class="card-map" :venue="store.current.venue" />

        <div class="swipe-hints" aria-hidden="true">
          <span :class="{ visible: swipeIntent === 'skip' }">Пропустить</span>
          <span :class="{ visible: swipeIntent === 'favorite' }">В избранное</span>
          <span :class="{ visible: swipeIntent === 'join' }">Записаться</span>
        </div>
      </article>
    </div>

    <div v-else-if="store.loading" class="empty-state">
      <div class="loader"></div>
      <p>Загружаем публикации...</p>
    </div>
    <div v-else-if="store.error" class="empty-state">
      <p>Не удалось загрузить ленту</p>
      <button @click="reload">Повторить</button>
    </div>
    <div v-else class="empty-state">
      <p>Новых публикаций пока нет</p>
      <button @click="reload">Обновить</button>
    </div>

    <p v-if="store.actionError" class="error">{{ store.actionError }}</p>

    <div class="actions" v-if="store.current">
      <button class="action-btn skip" :disabled="store.actionLoading" aria-label="Пропустить" @click="handleSkip">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M6 6l12 12M18 6 6 18" />
        </svg>
      </button>
      <button class="action-btn save" :disabled="store.actionLoading" aria-label="В избранное" @click="handleFavorite">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 4h10a1 1 0 0 1 1 1v16l-6-3.5L6 21V5a1 1 0 0 1 1-1Z" />
        </svg>
      </button>
      <button class="action-btn join" :disabled="store.actionLoading" aria-label="Записаться" @click="handleJoin">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20 6 9 17l-5-5" />
        </svg>
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import VenueMapPreview from "../components/VenueMapPreview.vue";
import { useEventsStore } from "../stores/events";

const store = useEventsStore();
const mode = ref("info");
const dragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const drag = ref({ x: 0, y: 0 });

onMounted(() => store.loadFeed({ reset: true }));

const formattedTime = computed(() => {
  if (!store.current?.scheduled_at) return "Время уточняется";
  return new Date(store.current.scheduled_at).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
});

const priceLabel = computed(() => {
  const price = Number(store.current?.price ?? store.current?.venue?.price);
  if (!Number.isFinite(price) || price <= 0) return "Бесплатно";
  return `${price.toLocaleString("ru-RU")} ₸`;
});

const cardNumber = computed(() => String(store.current?.id ?? 0).padStart(2, "0").slice(-2));

const swipeIntent = computed(() => {
  if (drag.value.y < -76) return "favorite";
  if (drag.value.x > 74) return "join";
  if (drag.value.x < -74) return "skip";
  return "";
});

const cardStyle = computed(() => ({
  transform: `translate3d(${drag.value.x}px, ${drag.value.y}px, 0) rotate(${drag.value.x * 0.035}deg)`,
}));

const ghostFrontStyle = computed(() => ({
  transform: `translate3d(10px, 12px, 0) scale(${0.96 + Math.min(Math.abs(drag.value.x) / 1600, 0.02)})`,
}));

const ghostBackStyle = computed(() => ({
  transform: "translate3d(20px, 25px, 0) scale(0.92)",
}));

function reload() {
  store.loadFeed({ reset: true });
}

function closeApp() {
  const tg = window.Telegram?.WebApp;
  if (tg?.close) tg.close();
  else window.history.back();
}

function startDrag(event) {
  if (event.target.closest("button, a, input, select, textarea")) return;
  if (event.pointerType === "mouse" && event.button !== 0) return;
  dragging.value = true;
  dragStart.value = { x: event.clientX, y: event.clientY };
  event.currentTarget.setPointerCapture?.(event.pointerId);
}

function moveDrag(event) {
  if (!dragging.value) return;
  drag.value = {
    x: event.clientX - dragStart.value.x,
    y: event.clientY - dragStart.value.y,
  };
}

async function endDrag() {
  if (!dragging.value) return;
  const intent = swipeIntent.value;
  cancelDrag();
  if (intent === "join") await handleJoin();
  if (intent === "favorite") await handleFavorite();
  if (intent === "skip") await handleSkip();
}

function cancelDrag() {
  dragging.value = false;
  drag.value = { x: 0, y: 0 };
}

async function handleJoin() {
  await store.join();
  mode.value = "info";
}

async function handleSkip() {
  await store.skip();
  mode.value = "info";
}

async function handleFavorite() {
  await store.favorite();
  mode.value = "info";
}
</script>

<style scoped>
.feed-screen {
  position: relative;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-height: 100svh;
  overflow: hidden;
  padding: 22px clamp(12px, 4vw, 30px) 20px;
  background:
    linear-gradient(90deg, rgba(17, 17, 17, 0.035) 1px, transparent 1px),
    linear-gradient(0deg, rgba(17, 17, 17, 0.035) 1px, transparent 1px),
    var(--surface-muted);
  background-size: 48px 48px;
}
.close-button {
  position: absolute;
  z-index: 12;
  top: 18px;
  right: 18px;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid var(--line-soft);
  border-radius: 50%;
  background: #fff;
  color: var(--text-main);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}
.close-button span {
  position: absolute;
  width: 18px;
  height: 2px;
  border-radius: 2px;
  background: currentColor;
}
.close-button span:first-child {
  transform: rotate(45deg);
}
.close-button span:last-child {
  transform: rotate(-45deg);
}
.feed-header {
  padding: 8px 52px 12px 0;
}
.feed-header p {
  margin: 0 0 6px;
  color: var(--text-faint);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.feed-header h1 {
  margin: 0;
  color: var(--text-main);
  font-size: clamp(26px, 7vw, 42px);
  line-height: 0.96;
}
.deck {
  position: relative;
  align-self: stretch;
  min-height: 0;
  margin: 4px 0 14px;
  touch-action: none;
}
.event-panel {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border: 1px solid var(--line-soft);
  border-radius: 30px;
  background: #fff;
  box-shadow: var(--shadow-floating);
}
.active-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 18px;
  cursor: grab;
  transition: transform 0.24s ease;
  user-select: none;
}
.dragging .active-card {
  cursor: grabbing;
  transition: none;
}
.ghost {
  pointer-events: none;
}
.ghost-front {
  opacity: 0.52;
  filter: saturate(0.75);
}
.ghost-back {
  opacity: 0.22;
  filter: saturate(0.55);
}
.top-row {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
.segmented {
  display: inline-flex;
  padding: 4px;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: var(--surface-soft);
}
.segmented button {
  min-width: 70px;
  padding: 9px 13px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 900;
}
.segmented button.active {
  background: var(--black);
  color: #fff;
}
.slots {
  display: grid;
  place-items: center;
  min-width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--line-soft);
  background: #fff;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 900;
}
.info-layout {
  position: relative;
  display: grid;
  grid-template-rows: minmax(180px, 42%) 1fr;
  gap: 18px;
  flex: 1;
  min-height: 0;
  margin-top: 18px;
}
.card-map {
  margin-top: 18px;
}
.venue-image {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line-soft);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.3), transparent 46%),
    linear-gradient(90deg, rgba(17, 17, 17, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(17, 17, 17, 0.08) 1px, transparent 1px),
    #e7e7e2;
  background-size: auto, 38px 38px, 38px 38px, auto;
}
.venue-image::before,
.venue-image::after {
  content: "";
  position: absolute;
  border-radius: 999px;
  background: var(--black);
  opacity: 0.84;
}
.venue-image::before {
  left: -16%;
  top: 52%;
  width: 136%;
  height: 14px;
  transform: rotate(-13deg);
}
.venue-image::after {
  right: 18%;
  top: -14%;
  width: 14px;
  height: 132%;
  transform: rotate(21deg);
}
.image-tag,
.image-number {
  position: absolute;
  z-index: 2;
}
.image-tag {
  top: 14px;
  left: 14px;
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.88);
  color: var(--text-main);
  font-size: 12px;
  font-weight: 900;
}
.image-number {
  right: 14px;
  bottom: 4px;
  color: rgba(17, 17, 17, 0.16);
  font-size: clamp(82px, 24vw, 160px);
  font-weight: 950;
  line-height: 0.9;
}
.info-content {
  position: relative;
  z-index: 2;
  width: 100%;
  padding: 0 2px 8px;
}
.sport {
  display: inline-flex;
  margin: 0 0 12px;
  padding: 8px 11px;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: #fff;
  color: var(--text-main);
  font-size: 12px;
  font-weight: 950;
}
h2 {
  max-width: 94%;
  margin: 0;
  color: var(--text-main);
  font-size: clamp(32px, 9vw, 58px);
  line-height: 0.92;
}
.address {
  max-width: 82%;
  margin: 12px 0 0;
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.35;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 18px;
}
.metrics div {
  min-width: 0;
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: 18px;
  background: var(--surface-muted);
}
.metrics span {
  display: block;
  margin-bottom: 6px;
  color: var(--text-faint);
  font-size: 11px;
  font-weight: 800;
}
.metrics strong {
  display: block;
  overflow-wrap: anywhere;
  color: var(--text-main);
  font-size: 13px;
  line-height: 1.15;
}
.swipe-hints {
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
}
.swipe-hints span {
  position: absolute;
  padding: 12px 14px;
  border: 2px solid currentColor;
  border-radius: 999px;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 950;
  opacity: 0;
  text-transform: uppercase;
  transition: opacity 0.12s ease;
}
.swipe-hints span.visible {
  opacity: 1;
}
.swipe-hints span:nth-child(1) {
  top: 50%;
  left: 18px;
  transform: rotate(-12deg);
}
.swipe-hints span:nth-child(2) {
  top: 80px;
  left: 50%;
  transform: translateX(-50%) rotate(-2deg);
}
.swipe-hints span:nth-child(3) {
  top: 50%;
  right: 18px;
  transform: rotate(12deg);
}
.empty-state {
  align-self: center;
  display: grid;
  place-items: center;
  gap: 14px;
  min-height: 54vh;
  text-align: center;
  color: var(--text-muted);
}
.empty-state button {
  padding: 12px 18px;
  border: 0;
  border-radius: 999px;
  background: var(--black);
  color: #fff;
  font-weight: 900;
}
.loader {
  width: 34px;
  height: 34px;
  border: 3px solid var(--line-soft);
  border-top-color: var(--black);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.error {
  margin: -6px 0 8px;
  color: #111;
  font-size: 13px;
  text-align: center;
}
.actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  justify-items: center;
}
.action-btn {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  border: 1px solid var(--line-soft);
  color: var(--text-main);
  box-shadow: var(--shadow-soft);
}
.action-btn svg {
  width: 25px;
  height: 25px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.action-btn:disabled {
  opacity: 0.65;
}
.skip {
  background: #fff;
}
.save {
  background: var(--surface-soft);
}
.save svg {
  fill: none;
}
.join {
  border-color: var(--black);
  background: var(--black);
  color: #fff;
}

@media (max-width: 430px) {
  .feed-screen {
    padding: 16px 10px 16px;
  }
  .feed-header {
    padding-top: 4px;
  }
  .deck {
    margin-top: 0;
  }
  .event-panel {
    border-radius: 24px;
  }
  .active-card {
    padding: 14px;
  }
  .segmented button {
    min-width: 58px;
    padding: 8px 10px;
  }
  .slots {
    min-width: 42px;
    height: 42px;
  }
  .info-layout {
    grid-template-rows: minmax(160px, 40%) 1fr;
    gap: 14px;
  }
  .metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .metrics div {
    padding: 10px 8px;
  }
  .actions {
    gap: 8px;
  }
  .action-btn {
    width: 54px;
    height: 54px;
  }
}
</style>
