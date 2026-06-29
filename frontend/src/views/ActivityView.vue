<template>
  <section v-if="!mapOpen" class="activity-page activity-home">
    <section class="runna-calendar">
      <header class="activity-top">
        <div>
          <p>{{ monthLabel }}</p>
          <h1>Сегодня</h1>
        </div>
        <button class="streak-pill" type="button">
          <strong>{{ streakCount }}</strong>
          <span>стрик</span>
        </button>
      </header>

      <section class="week-strip" aria-label="Календарь активности">
        <button
          v-for="day in weekDays"
          :key="day.key"
          class="day-cell"
          :class="{ today: day.isToday, checked: day.checked }"
          type="button"
        >
          <span>{{ day.weekday }}</span>
          <strong>{{ day.day }}</strong>
          <i aria-hidden="true"></i>
        </button>
      </section>
    </section>

    <section class="home-stage">
      <div class="spin-badge" aria-hidden="true">
        <span></span>
      </div>
      <h2>{{ greeting }}, {{ userName }}</h2>
      <p>Начните тренировку или выберите площадку рядом</p>
    </section>

    <section class="home-insight">
      <button type="button" aria-label="Закрыть подсказку">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
      </button>
      <div>
        <h3>Стрик начинается с чек-ина</h3>
        <p>Отметьтесь рядом с площадкой, чтобы день засчитался в календаре.</p>
      </div>
    </section>

    <button class="start-workout" type="button" @click="openMap">
      <span aria-hidden="true"></span>
      Начать тренировку
    </button>
  </section>

  <section v-else class="map-experience" aria-label="Карта площадок">
    <div class="map-canvas fullscreen">
      <div ref="googleMapEl" class="google-map" :class="{ ready: isGoogleMapReady }"></div>
      <div v-if="!isGoogleMapReady" class="map-grid" aria-hidden="true"></div>
      <div v-if="!isGoogleMapReady" class="route route-a" aria-hidden="true"></div>
      <div v-if="!isGoogleMapReady" class="route route-b" aria-hidden="true"></div>
      <div
        v-if="!isGoogleMapReady"
        class="user-dot"
        :class="{ located: userPosition }"
        aria-label="Вы здесь"
      ></div>

      <div class="map-topbar">
        <button class="map-back" type="button" aria-label="Назад" @click="closeMap">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6" /></svg>
        </button>
        <button class="search-pill" type="button" @click="sheetState = 'expanded'">
          <strong>{{ selectedVenue?.city || "Тараз" }}: площадки</strong>
          <span>Сегодня · кто играет?</span>
        </button>
        <button class="tune-button" type="button" aria-label="Фильтры">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M7 7v10M4 17h16M17 7v10" /></svg>
        </button>
      </div>

      <button
        class="locate-button fire-button"
        type="button"
        :class="{ checking: checkinLoading || locating }"
        :disabled="checkinLoading || locating"
        aria-label="Записать стрик рядом с площадкой"
        @click="handleFireCheckin"
      >
        <span aria-hidden="true">🔥</span>
      </button>

      <div class="map-filter-bar" aria-label="Фильтры площадок на карте">
        <button
          v-for="filter in filters"
          :key="filter.id"
          :class="{ active: activeFilter === filter.id }"
          type="button"
          @click="activeFilter = filter.id"
        >
          {{ filter.label }}
        </button>
      </div>

      <template v-if="!isGoogleMapReady">
        <div
          v-for="venue in rankedVenues"
          :key="`radius-${venue.id}`"
          class="venue-radius"
          :class="{ active: selectedVenue?.id === venue.id }"
          :style="{ left: `${venue.mapX}%`, top: `${venue.mapY}%` }"
          aria-hidden="true"
        ></div>
        <button
          v-for="venue in rankedVenues"
          :key="venue.id"
          class="venue-pin"
          :class="{ active: selectedVenue?.id === venue.id, busy: venue.load > 70 }"
          type="button"
          :style="{ left: `${venue.mapX}%`, top: `${venue.mapY}%` }"
          @click="selectedVenue = venue"
        >
          {{ venue.is_paid ? `${venue.price}₸` : venue.distanceLabel }}
        </button>
      </template>
      <p v-if="mapMessage" class="map-message">{{ mapMessage }}</p>
    </div>

    <article
      v-if="selectedVenue"
      class="venue-sheet"
      :class="{ expanded: sheetState === 'expanded' }"
      @click.self="sheetState = sheetState === 'expanded' ? 'collapsed' : 'expanded'"
    >
      <button class="sheet-handle" type="button" aria-label="Переключить шторку" @click="toggleSheet"></button>

      <div v-if="sheetState === 'collapsed'" class="sheet-summary" @click="sheetState = 'expanded'">
        <strong>{{ rankedVenues.length }} площадки рядом</strong>
        <span>{{ selectedVenue.name }} · {{ selectedVenue.distanceLabel }}</span>
      </div>

      <template v-else>
        <div class="sheet-title">
          <div>
            <p>{{ selectedVenue.sport_type || "Площадка" }} · {{ selectedVenue.loadLabel }}</p>
            <h2>{{ rankedVenues.length }} площадки рядом</h2>
          </div>
          <button type="button" aria-label="Свернуть" @click="sheetState = 'collapsed'">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
        </div>

        <div class="property-card">
          <div class="venue-photo" aria-hidden="true">
            <span>{{ selectedVenue.sport_type?.slice(0, 1) || "D" }}</span>
            <button type="button" aria-label="В избранное">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z" /></svg>
            </button>
          </div>
          <div class="property-copy">
            <h3>{{ selectedVenue.name }}</h3>
            <p>{{ selectedVenue.address || "Адрес уточняется" }}</p>
          </div>
        </div>

        <div class="load-meter" aria-label="Загрузка площадки">
          <span :style="{ width: `${selectedVenue.load}%` }"></span>
        </div>
        <div class="venue-metrics">
          <span><strong>{{ selectedVenue.distanceLabel }}</strong><small>от вас</small></span>
          <span><strong>{{ selectedVenue.load }}%</strong><small>загрузка</small></span>
          <span><strong>{{ selectedVenue.is_paid ? `${selectedVenue.price}₸` : "0₸" }}</strong><small>вход</small></span>
        </div>
        <div class="venue-actions">
          <button type="button" @click="goCreate(selectedVenue)">Найти игроков</button>
        </div>
        <p v-if="checkinMessage" class="checkin-message">{{ checkinMessage }}</p>
      </template>
    </article>

    <Transition name="streak-pop">
      <div v-if="showCheckinSuccess" class="checkin-celebration" role="status">
        <div class="celebration-card">
          <div class="celebration-flame" aria-hidden="true">🔥</div>
          <p>Стрик записан</p>
          <strong>Вы рядом с площадкой</strong>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { createCheckin } from "../api/checkins";
import { getVenues } from "../api/events";
import { DEMO_EVENTS, isLocalDemoMode } from "../stores/events";
import { useUserStore } from "../stores/user";

const TARAZ_CENTER = { lat: 42.9007, lng: 71.3658 };
const CHECKIN_KEY = "draftspot:checkins";
const CHECKIN_RADIUS_METERS = 200;

const router = useRouter();
const userStore = useUserStore();
const venues = ref([]);
const mode = ref("map");
const mapOpen = ref(false);
const sheetState = ref("collapsed");
const activeFilter = ref("near");
const selectedVenue = ref(null);
const checkinLoading = ref(false);
const checkinMessage = ref("");
const checkins = ref(readCheckins());
const googleMapEl = ref(null);
const googleMap = ref(null);
const googleOverlays = ref([]);
const googleUserOverlay = ref(null);
const isGoogleMapReady = ref(false);
const mapMessage = ref("");
const locating = ref(false);
const userPosition = ref(null);
const showCheckinSuccess = ref(false);

const filters = [
  { id: "near", label: "Рядом" },
  { id: "busy", label: "Загрузка" },
  { id: "free", label: "Бесплатно" },
];

const monthLabel = computed(() =>
  new Intl.DateTimeFormat("ru-RU", { month: "long", year: "numeric" }).format(new Date())
);

const weekDays = computed(() => {
  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - 3);

  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    const key = date.toISOString().slice(0, 10);
    return {
      key,
      day: date.getDate(),
      checked: Object.values(checkins.value).some((item) => item.date === key),
      isToday: key === today.toISOString().slice(0, 10),
      weekday: new Intl.DateTimeFormat("ru-RU", { weekday: "short" }).format(date).slice(0, 2),
    };
  });
});

const streakCount = computed(() => {
  const checkedDates = new Set(Object.values(checkins.value).map((item) => item.date));
  let count = 0;
  const cursor = new Date();
  while (checkedDates.has(cursor.toISOString().slice(0, 10))) {
    count += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return count;
});

const enrichedVenues = computed(() =>
  venues.value.map((venue, index) => {
    const distance = distanceKm(TARAZ_CENTER, { lat: venue.latitude, lng: venue.longitude });
    const load = [38, 74, 57, 86, 29][Math.abs(Number(venue.id)) % 5] ?? 45;
    return {
      ...venue,
      distance,
      load,
      loadLabel: load > 70 ? "оживленно" : load > 45 ? "средне" : "свободно",
      distanceLabel: distance < 1 ? `${Math.round(distance * 1000)} м` : `${distance.toFixed(1)} км`,
      mapX: [24, 68, 42, 78, 54][index % 5],
      mapY: [58, 34, 72, 62, 46][index % 5],
    };
  })
);

const rankedVenues = computed(() => {
  const items = [...enrichedVenues.value];
  if (activeFilter.value === "busy") return items.sort((a, b) => b.load - a.load);
  if (activeFilter.value === "free") return items.filter((venue) => !venue.is_paid).sort((a, b) => a.distance - b.distance);
  return items.sort((a, b) => a.distance - b.distance);
});

const googleMapsKey = computed(() => import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? "");
const userName = computed(() => userStore.profile?.name || "Aksunkar");
const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return "Доброе утро";
  if (hour < 18) return "Добрый день";
  return "Добрый вечер";
});

function readCheckins() {
  try {
    return JSON.parse(localStorage.getItem(CHECKIN_KEY) || "{}");
  } catch {
    return {};
  }
}

function writeCheckins(value) {
  localStorage.setItem(CHECKIN_KEY, JSON.stringify(value));
}

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function distanceKm(from, to) {
  const toRad = (value) => (Number(value) * Math.PI) / 180;
  const lat1 = toRad(from.lat);
  const lat2 = toRad(to.lat);
  const deltaLat = toRad(to.lat - from.lat);
  const deltaLng = toRad(to.lng - from.lng);
  const a =
    Math.sin(deltaLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(deltaLng / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function goCreate(venue) {
  router.push({ name: "create-event", query: { venue: venue.id } });
}

async function openMap() {
  mapOpen.value = true;
  mode.value = "map";
  sheetState.value = "collapsed";
  await nextTick();
  await initGoogleMap();
}

function closeMap() {
  mapOpen.value = false;
  sheetState.value = "collapsed";
  destroyGoogleMap();
}

function toggleSheet() {
  sheetState.value = sheetState.value === "expanded" ? "collapsed" : "expanded";
}

async function locateUser() {
  locating.value = true;
  mapMessage.value = "";
  try {
    const position = await readPosition();
    userPosition.value = {
      lat: position.coords.latitude,
      lng: position.coords.longitude,
    };
    mapMessage.value = "Геолокация получена";
    updateUserMarker();
  } catch {
    mapMessage.value = "Не удалось получить геолокацию";
  } finally {
    locating.value = false;
  }
}

async function handleFireCheckin() {
  if (!selectedVenue.value) {
    await locateUser();
    return;
  }
  await checkIn(selectedVenue.value);
}

async function checkIn(venue) {
  checkinLoading.value = true;
  checkinMessage.value = "";
  mapMessage.value = "";
  try {
    const position = await readPosition();
    userPosition.value = {
      lat: position.coords.latitude,
      lng: position.coords.longitude,
    };
    updateUserMarker();

    const km = distanceKm(
      { lat: position.coords.latitude, lng: position.coords.longitude },
      { lat: venue.latitude, lng: venue.longitude }
    );
    const distanceMeters = Math.round(km * 1000);
    if (distanceMeters > CHECKIN_RADIUS_METERS) {
      const distanceLabel = distanceMeters >= 1000 ? `${km.toFixed(1)} км` : `${distanceMeters} м`;
      checkinMessage.value = `Пока стрик не записан: вы не рядом с площадкой (${distanceLabel}).`;
      return;
    }

    let result = null;
    try {
      result = await createCheckin({
        venue_id: venue.id,
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      });
    } catch (error) {
      if (!isLocalDemoMode()) {
        checkinMessage.value = "Сервер не записал стрик. Попробуйте ещё раз рядом с площадкой.";
        return;
      }
    }

    if (result && !result.checked_in) {
      checkinMessage.value = `Пока стрик не записан: вы не рядом с площадкой (${result.distance_meters} м).`;
      return;
    }

    saveCheckin(venue, result?.distance_meters ?? distanceMeters);
    checkinMessage.value = result ? "Стрик записан" : "Стрик записан локально";
    showSuccessAnimation();
  } catch {
    checkinMessage.value = "Не удалось получить геолокацию. Стрик пока не записан.";
  } finally {
    checkinLoading.value = false;
  }
}

function saveCheckin(venue, distanceMeters = null) {
  checkins.value = {
    ...checkins.value,
    [venue.id]: {
      date: todayKey(),
      venue_id: venue.id,
      venue_name: venue.name,
      distance_meters: distanceMeters,
    },
  };
  writeCheckins(checkins.value);
}

function showSuccessAnimation() {
  showCheckinSuccess.value = true;
  window.setTimeout(() => {
    showCheckinSuccess.value = false;
  }, 2200);
}

function readPosition() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("geolocation unavailable"));
      return;
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      maximumAge: 30_000,
      timeout: 8_000,
    });
  });
}

async function loadVenues() {
  try {
    if (isLocalDemoMode()) throw new Error("demo");
    venues.value = await getVenues();
  } catch {
    venues.value = DEMO_EVENTS.map((event) => event.venue);
  } finally {
    selectedVenue.value = rankedVenues.value[0] ?? null;
    if (mapOpen.value) {
      await nextTick();
      await initGoogleMap();
    }
  }
}

function loadGoogleMaps() {
  if (!googleMapsKey.value) {
    mapMessage.value = "Добавьте VITE_GOOGLE_MAPS_API_KEY для Google Maps";
    return Promise.reject(new Error("missing google maps key"));
  }
  if (window.google?.maps) return Promise.resolve(window.google.maps);
  if (window.__draftspotGoogleMapsPromise) return window.__draftspotGoogleMapsPromise;

  const existingScript = document.querySelector("script[data-draftspot-google-maps]");
  existingScript?.remove();

  window.__draftspotGoogleMapsPromise = new Promise((resolve, reject) => {
    window.__draftspotInitGoogleMaps = () => {
      resolve(window.google.maps);
    };
    const script = document.createElement("script");
    script.dataset.draftspotGoogleMaps = "true";
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(googleMapsKey.value)}&callback=__draftspotInitGoogleMaps&loading=async&v=weekly`;
    script.async = true;
    script.defer = true;
    script.addEventListener("error", (error) => {
      window.__draftspotGoogleMapsPromise = null;
      reject(error);
    }, { once: true });
    document.head.appendChild(script);
  });
  return window.__draftspotGoogleMapsPromise;
}

async function initGoogleMap() {
  if (!googleMapEl.value || googleMap.value || mode.value !== "map" || !mapOpen.value) return;
  try {
    const maps = await loadGoogleMaps();
    googleMap.value = new maps.Map(googleMapEl.value, {
      center: TARAZ_CENTER,
      clickableIcons: false,
      disableDefaultUI: true,
      fullscreenControl: false,
      gestureHandling: "greedy",
      mapTypeControl: false,
      streetViewControl: false,
      styles: [
        { elementType: "geometry", stylers: [{ color: "#ebece8" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#5d665f" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#f7f8f5" }] },
        { featureType: "poi", stylers: [{ visibility: "off" }] },
        { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
        { featureType: "road.arterial", elementType: "geometry", stylers: [{ color: "#d8dcd5" }] },
        { featureType: "water", elementType: "geometry", stylers: [{ color: "#cbdeda" }] },
      ],
      zoom: 13,
    });
    isGoogleMapReady.value = true;
    mapMessage.value = "";
    syncGoogleMarkers();
    updateUserMarker();
  } catch {
    isGoogleMapReady.value = false;
  }
}

function destroyGoogleMap() {
  googleOverlays.value.forEach((overlay) => overlay.setMap(null));
  googleOverlays.value = [];
  googleUserOverlay.value?.setMap(null);
  googleUserOverlay.value = null;
  googleMap.value = null;
  isGoogleMapReady.value = false;
}

function syncGoogleMarkers() {
  if (!googleMap.value || !window.google?.maps) return;
  googleOverlays.value.forEach((overlay) => overlay.setMap(null));
  googleOverlays.value = rankedVenues.value.flatMap((venue) => {
    const active = selectedVenue.value?.id === venue.id;
    const label = venue.is_paid ? `${venue.price}₸` : venue.distanceLabel;
    const position = { lat: Number(venue.latitude), lng: Number(venue.longitude) };
    return [
      createRadiusOverlay({
        active,
        map: googleMap.value,
        position,
        radiusMeters: CHECKIN_RADIUS_METERS,
      }),
      createMapOverlay({
        className: `map-price-marker${active ? " active" : ""}${venue.load > 70 ? " busy" : ""}`,
        html: `<strong>${label}</strong><small>${venue.load}%</small>`,
        map: googleMap.value,
        position,
        title: `${venue.name}, ${venue.distanceLabel}`,
        onClick: () => {
          selectedVenue.value = venue;
          googleMap.value.panTo(position);
        },
      }),
    ];
  });
}

function createMapOverlay({ className, html, map, onClick, position, title }) {
  const overlay = new window.google.maps.OverlayView();
  let element = null;

  overlay.onAdd = () => {
    element = document.createElement("button");
    element.type = "button";
    element.className = className;
    element.innerHTML = html;
    element.title = title || "";
    element.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      onClick?.();
    });
    overlay.getPanes().overlayMouseTarget.appendChild(element);
  };

  overlay.draw = () => {
    if (!element) return;
    const point = overlay
      .getProjection()
      .fromLatLngToDivPixel(new window.google.maps.LatLng(position.lat, position.lng));
    if (!point) return;
    element.style.left = `${point.x}px`;
    element.style.top = `${point.y}px`;
  };

  overlay.onRemove = () => {
    element?.remove();
    element = null;
  };

  overlay.setMap(map);
  return overlay;
}

function createRadiusOverlay({ active, map, position, radiusMeters }) {
  const overlay = new window.google.maps.OverlayView();
  let element = null;

  overlay.onAdd = () => {
    element = document.createElement("div");
    element.className = `map-radius-overlay${active ? " active" : ""}`;
    overlay.getPanes().overlayLayer.appendChild(element);
  };

  overlay.draw = () => {
    if (!element) return;
    const projection = overlay.getProjection();
    const center = projection.fromLatLngToDivPixel(
      new window.google.maps.LatLng(position.lat, position.lng)
    );
    const lngOffset = radiusMeters / (111_320 * Math.cos((position.lat * Math.PI) / 180));
    const edge = projection.fromLatLngToDivPixel(
      new window.google.maps.LatLng(position.lat, position.lng + lngOffset)
    );
    if (!center || !edge) return;
    const radiusPx = Math.max(Math.abs(edge.x - center.x), 24);
    element.style.left = `${center.x - radiusPx}px`;
    element.style.top = `${center.y - radiusPx}px`;
    element.style.width = `${radiusPx * 2}px`;
    element.style.height = `${radiusPx * 2}px`;
  };

  overlay.onRemove = () => {
    element?.remove();
    element = null;
  };

  overlay.setMap(map);
  return overlay;
}

function updateUserMarker() {
  if (!googleMap.value || !window.google?.maps || !userPosition.value) return;
  googleUserOverlay.value?.setMap(null);
  googleUserOverlay.value = createMapOverlay({
    className: "map-user-marker",
    html: "<span></span>",
    map: googleMap.value,
    position: userPosition.value,
    title: "Вы здесь",
    onClick: () => {
      googleMap.value.panTo(userPosition.value);
    },
  });
  googleMap.value.panTo(userPosition.value);
}

watch(mode, async (value) => {
  if (value === "map" && mapOpen.value) {
    await nextTick();
    await initGoogleMap();
  }
});

watch(mapOpen, async (value) => {
  if (value) {
    await nextTick();
    await initGoogleMap();
  }
});

watch(rankedVenues, syncGoogleMarkers);
watch(selectedVenue, () => {
  syncGoogleMarkers();
  if (googleMap.value && selectedVenue.value) {
    googleMap.value.panTo({
      lat: Number(selectedVenue.value.latitude),
      lng: Number(selectedVenue.value.longitude),
    });
  }
});

onMounted(loadVenues);
</script>

<style scoped>
.activity-page {
  min-height: 100svh;
  padding: 0 16px 34px;
  background: #f6f7f5;
  color: #111;
}
.runna-calendar {
  margin: 0 -16px;
  padding: 14px 16px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0 0 16px 16px;
  background: #222835;
  color: #fff;
  box-shadow: 0 10px 24px rgba(17, 17, 17, 0.1);
}
.activity-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 760px;
  margin: 0 auto 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.activity-top p {
  margin: 0 0 2px;
  color: #8d96a7;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}
.activity-top h1 {
  margin: 0;
  color: #fff;
  font-size: 24px;
  line-height: 1;
}
.streak-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 11px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
.streak-pill strong {
  font-size: 16px;
}
.streak-pill span {
  color: #c9cfda;
  font-size: 12px;
  font-weight: 850;
}
.week-strip {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 4px;
  max-width: 760px;
  margin: 0 auto;
  padding: 0;
  border: none;
  border-radius: 0;
  background: transparent;
}
.day-cell {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 5px;
  min-width: 0;
  min-height: 48px;
  padding: 5px 0 6px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #8d96a7;
}
.day-cell strong {
  color: #f4f6fb;
  font-size: 17px;
  line-height: 1;
}
.day-cell span {
  color: #8d96a7;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}
.day-cell i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: transparent;
}
.day-cell.today {
  background: #f4f6fb;
  color: #222835;
}
.day-cell.today strong {
  color: #222835;
}
.day-cell.today span {
  color: #222835;
}
.day-cell.checked i {
  background: #2f9e68;
}
.day-cell.today.checked i {
  background: #2f9e68;
}
.mode-row,
.filters {
  gap: 8px;
  max-width: 760px;
  margin: 0 auto 10px;
}
.mode-row {
  display: flex;
  padding: 4px;
  border: 1px solid #dfe5df;
  border-radius: 999px;
  background: #fff;
}
.filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.mode-row button,
.filters button {
  border: none;
  font-weight: 900;
}
.mode-row button {
  flex: 1;
  min-height: 40px;
  border-radius: 999px;
  background: transparent;
  color: #69716d;
}
.mode-row button.active {
  background: #111;
  color: #fff;
}
.filters button {
  min-width: 0;
  min-height: 38px;
  padding: 0 8px;
  border: 1px solid #dfe5df;
  border-radius: 999px;
  background: #fff;
  color: #111;
  overflow: hidden;
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.filters button.active {
  border-color: #111;
  background: #111;
  color: #fff;
}
.map-panel,
.venue-list {
  max-width: 760px;
  margin: 0 auto;
}
.map-canvas {
  position: relative;
  height: min(58svh, 520px);
  min-height: 390px;
  overflow: hidden;
  border: 1px solid #dfe5df;
  border-radius: 28px;
  background:
    radial-gradient(circle at 42% 55%, rgba(47, 158, 104, 0.18), transparent 0 62px, transparent 63px),
    linear-gradient(145deg, #e9ece7, #f9faf8);
}
.google-map {
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 0;
  transition: opacity 0.25s ease;
}
.google-map.ready {
  opacity: 1;
}
.map-grid {
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    linear-gradient(90deg, rgba(17, 17, 17, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(17, 17, 17, 0.08) 1px, transparent 1px);
  background-size: 46px 46px;
}
.route {
  position: absolute;
  z-index: 2;
  border-radius: 999px;
  background: rgba(17, 17, 17, 0.18);
}
.route-a {
  left: -10%;
  top: 45%;
  width: 130%;
  height: 15px;
  transform: rotate(-17deg);
}
.route-b {
  left: 58%;
  top: -8%;
  width: 14px;
  height: 116%;
  transform: rotate(25deg);
}
.user-dot {
  position: absolute;
  z-index: 4;
  left: 46%;
  top: 55%;
  width: 24px;
  height: 24px;
  border: 4px solid #fff;
  border-radius: 50%;
  background: #1d9bf0;
  box-shadow: 0 0 0 12px rgba(29, 155, 240, 0.16), 0 12px 30px rgba(29, 155, 240, 0.32);
}
.user-dot.located {
  box-shadow: 0 0 0 16px rgba(47, 158, 104, 0.18), 0 12px 30px rgba(47, 158, 104, 0.28);
}
.locate-button {
  position: absolute;
  z-index: 8;
  top: 14px;
  right: 14px;
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border: 1px solid rgba(17, 17, 17, 0.1);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
  color: #111;
  box-shadow: 0 12px 28px rgba(17, 17, 17, 0.12);
}
.fire-button {
  border-color: rgba(255, 128, 109, 0.36);
  background:
    radial-gradient(circle at 50% 34%, #fff7b2 0 10px, transparent 11px),
    linear-gradient(145deg, #ff6b35, #f7b733);
  color: #111;
}
.fire-button span {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.28);
  font-size: 22px;
  line-height: 1;
  transform-origin: 50% 80%;
}
.fire-button.checking span {
  animation: flame-bounce 0.62s ease-in-out infinite alternate;
}
.locate-button:disabled {
  opacity: 0.7;
}
.map-filter-bar {
  position: absolute;
  z-index: 8;
  top: 14px;
  right: 70px;
  left: 14px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 7px;
}
.map-filter-bar button {
  min-width: 0;
  min-height: 42px;
  padding: 0 8px;
  border: 1px solid rgba(17, 17, 17, 0.1);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  color: #111;
  overflow: hidden;
  font-size: 13px;
  font-weight: 950;
  text-overflow: ellipsis;
  white-space: nowrap;
  box-shadow: 0 12px 28px rgba(17, 17, 17, 0.1);
}
.map-filter-bar button.active {
  background: #111;
  color: #fff;
}
.venue-pin {
  position: absolute;
  z-index: 5;
  min-width: 70px;
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid rgba(17, 17, 17, 0.14);
  border-radius: 999px;
  background: #fff;
  color: #111;
  font-size: 13px;
  font-weight: 950;
  box-shadow: 0 12px 28px rgba(17, 17, 17, 0.13);
  transform: translate(-50%, -50%);
}
.venue-pin.active {
  background: #111;
  color: #fff;
}
.venue-pin.busy:not(.active) {
  border-color: #ff806d;
}
.venue-radius {
  position: absolute;
  z-index: 3;
  width: 132px;
  height: 132px;
  border: 2px dashed rgba(47, 158, 104, 0.58);
  border-radius: 50%;
  background: rgba(47, 158, 104, 0.08);
  transform: translate(-50%, -50%);
}
.venue-radius.active {
  border-color: rgba(255, 107, 53, 0.86);
  background: rgba(255, 107, 53, 0.1);
}
:global(.map-radius-overlay) {
  position: absolute;
  border: 2px dashed rgba(47, 158, 104, 0.62);
  border-radius: 50%;
  background: rgba(47, 158, 104, 0.08);
  pointer-events: none;
}
:global(.map-radius-overlay.active) {
  border-color: rgba(255, 107, 53, 0.86);
  background: rgba(255, 107, 53, 0.1);
}
:global(.map-price-marker) {
  position: absolute;
  display: inline-grid;
  grid-template-columns: auto auto;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 11px;
  border: 1px solid rgba(17, 17, 17, 0.14);
  border-radius: 999px;
  background: #fff;
  color: #111;
  box-shadow: 0 12px 26px rgba(17, 17, 17, 0.2);
  cursor: pointer;
  font: inherit;
  transform: translate(-50%, -50%);
  transition: transform 0.16s ease, background 0.16s ease, color 0.16s ease;
  white-space: nowrap;
}
:global(.map-price-marker strong) {
  font-size: 13px;
  font-weight: 950;
}
:global(.map-price-marker small) {
  display: inline-grid;
  place-items: center;
  min-width: 28px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: #f0f2ef;
  color: #69716d;
  font-size: 10px;
  font-weight: 950;
}
:global(.map-price-marker.active) {
  z-index: 20;
  background: #111;
  color: #fff;
  transform: translate(-50%, -50%) scale(1.08);
}
:global(.map-price-marker.active small) {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}
:global(.map-price-marker.busy:not(.active)) {
  border-color: #ff806d;
}
:global(.map-user-marker) {
  position: absolute;
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border: 4px solid #fff;
  border-radius: 50%;
  background: #1d9bf0;
  box-shadow: 0 0 0 16px rgba(29, 155, 240, 0.16), 0 14px 34px rgba(29, 155, 240, 0.38);
  cursor: pointer;
  transform: translate(-50%, -50%);
}
:global(.map-user-marker span) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
}
.map-message {
  position: absolute;
  z-index: 8;
  right: 14px;
  bottom: 14px;
  left: 14px;
  margin: 0;
  padding: 10px 12px;
  border: 1px solid rgba(17, 17, 17, 0.08);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  color: #111;
  font-size: 13px;
  font-weight: 850;
  box-shadow: 0 12px 28px rgba(17, 17, 17, 0.1);
}
.venue-sheet {
  position: relative;
  z-index: 10;
  display: grid;
  gap: 13px;
  margin: -116px 14px 0;
  padding: 14px;
  border: 1px solid #dfe5df;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 22px 58px rgba(17, 17, 17, 0.16);
}
.sheet-handle {
  justify-self: center;
  width: 48px;
  height: 5px;
  border-radius: 999px;
  background: #d7ddd7;
}
.sheet-close {
  position: absolute;
  top: 12px;
  right: 12px;
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #111;
}
.sheet-close svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
}
.venue-photo {
  display: grid;
  place-items: center;
  height: 132px;
  border-radius: 18px;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.2) 50%, transparent 50%),
    linear-gradient(0deg, rgba(255, 255, 255, 0.2) 50%, transparent 50%),
    #7ed8cc;
  background-size: 44px 44px;
}
.venue-photo span {
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: #111;
  color: #fff;
  font-size: 24px;
  font-weight: 950;
}
.venue-sheet h2 {
  margin: 0 0 5px;
  font-size: 22px;
  line-height: 1.08;
}
.venue-eyebrow {
  margin: 0 0 5px;
  color: #69716d;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}
.venue-sheet p {
  margin: 0;
  color: #69716d;
  font-size: 14px;
}
.load-meter {
  overflow: hidden;
  height: 8px;
  border-radius: 999px;
  background: #edf0ec;
}
.load-meter span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #2f9e68, #ff806d);
}
.venue-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}
.venue-metrics span {
  min-width: 0;
  padding: 10px;
  border-radius: 16px;
  background: #f3f5f2;
}
.venue-metrics strong,
.venue-metrics small {
  display: block;
}
.venue-metrics strong {
  font-size: 17px;
}
.venue-metrics small {
  margin-top: 2px;
  color: #69716d;
  font-size: 11px;
  font-weight: 850;
}
.venue-actions {
  display: grid;
}
.venue-actions button {
  min-height: 48px;
  border: none;
  border-radius: 999px;
  background: #111;
  color: #fff;
  font-weight: 950;
}
.venue-actions button:disabled {
  opacity: 0.7;
}
.checkin-message {
  padding: 10px 12px;
  border-radius: 14px;
  background: #f3f5f2;
  color: #111;
  font-weight: 850;
}
.checkin-celebration {
  position: fixed;
  z-index: 50;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(17, 17, 17, 0.22);
}
.celebration-card {
  display: grid;
  justify-items: center;
  gap: 9px;
  width: min(280px, 100%);
  padding: 26px 18px 24px;
  border: 1px solid rgba(255, 128, 109, 0.34);
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 26px 80px rgba(17, 17, 17, 0.22);
  animation: celebration-pop 0.72s cubic-bezier(0.2, 0.95, 0.26, 1.12);
}
.celebration-flame {
  display: grid;
  place-items: center;
  width: 86px;
  height: 86px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 34%, #fff7b2 0 18px, transparent 19px),
    linear-gradient(145deg, #ff6b35, #f7b733);
  font-size: 52px;
  animation: flame-bounce 0.58s ease-in-out infinite alternate;
}
.celebration-card p {
  margin: 4px 0 0;
  color: #ff6b35;
  font-size: 14px;
  font-weight: 950;
  text-transform: uppercase;
}
.celebration-card strong {
  font-size: 22px;
  line-height: 1.08;
  text-align: center;
}
.streak-pop-enter-active,
.streak-pop-leave-active {
  transition: opacity 0.18s ease;
}
.streak-pop-enter-from,
.streak-pop-leave-to {
  opacity: 0;
}
.venue-list {
  display: grid;
  gap: 10px;
}
.venue-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  min-height: 76px;
  padding: 12px;
  border: 1px solid #dfe5df;
  border-radius: 20px;
  background: #fff;
  color: #111;
  text-align: left;
}
.row-avatar {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: #7ed8cc;
  font-weight: 950;
}
.venue-row strong,
.venue-row small {
  display: block;
}
.venue-row strong {
  overflow: hidden;
  font-size: 16px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.venue-row small {
  margin-top: 4px;
  color: #69716d;
}
.venue-row i {
  color: #69716d;
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}
.activity-home {
  position: relative;
  display: grid;
  grid-template-rows: auto minmax(320px, 1fr) auto;
  padding-bottom: 112px;
}
.home-stage {
  display: grid;
  place-items: center;
  align-content: center;
  min-height: 40svh;
  max-width: 760px;
  margin: 28px auto 0;
  text-align: center;
}
.spin-badge {
  position: relative;
  display: grid;
  place-items: center;
  width: 156px;
  height: 156px;
  margin-bottom: 26px;
  border-radius: 50%;
  background:
    conic-gradient(from 0deg, rgba(255, 128, 109, 0.84), rgba(126, 216, 204, 0.7), rgba(47, 158, 104, 0.8), rgba(255, 128, 109, 0.84));
  box-shadow: 0 22px 54px rgba(17, 17, 17, 0.1);
  animation: spinBadge 7.5s cubic-bezier(0.45, 0, 0.35, 1) infinite;
}
.spin-badge::before {
  position: absolute;
  inset: 22px;
  border-radius: inherit;
  background: #f6f7f5;
  content: "";
}
.spin-badge span {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 92px;
  height: 92px;
  border: none;
  border-radius: 50%;
  background: #fff;
  color: #111;
  box-shadow: inset 0 0 0 1px rgba(17, 17, 17, 0.05);
}
.spin-badge span::before {
  color: currentColor;
  content: "C";
  font-size: 54px;
  font-weight: 900;
  line-height: 1;
}
.home-stage h2 {
  margin: 0;
  color: #111;
  font-size: clamp(30px, 5vw, 44px);
  line-height: 1.05;
}
.home-stage p {
  margin: 10px 0 0;
  color: #69716d;
  max-width: 520px;
  font-size: 17px;
  font-weight: 800;
  line-height: 1.25;
}
.home-insight {
  position: relative;
  display: grid;
  max-width: 760px;
  margin: 12px auto 0;
  padding: 22px 58px 22px 22px;
  border: 1px solid #dfe5df;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 18px 44px rgba(17, 17, 17, 0.08);
}
.home-insight button {
  position: absolute;
  top: 14px;
  right: 14px;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: #f0f2ef;
  color: #111;
}
.home-insight svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.3;
  stroke-linecap: round;
}
.home-insight h3 {
  margin: 0 0 8px;
  font-size: 21px;
  line-height: 1.1;
}
.home-insight p {
  margin: 0;
  color: #69716d;
  line-height: 1.45;
}
.start-workout {
  position: fixed;
  z-index: 35;
  right: 16px;
  bottom: max(18px, env(safe-area-inset-bottom));
  left: 88px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 11px;
  min-height: 58px;
  max-width: 760px;
  margin: 0 auto;
  border: none;
  border-radius: 999px;
  background: #111;
  color: #fff;
  font-size: 17px;
  font-weight: 900;
  box-shadow: 0 14px 34px rgba(17, 17, 17, 0.16);
}
.start-workout span {
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 13px solid currentColor;
}
.map-experience {
  position: fixed;
  z-index: 90;
  inset: 0;
  overflow: hidden;
  background: #fff;
  color: #111;
}
.map-canvas.fullscreen {
  position: absolute;
  inset: 0;
  width: 100%;
  height: auto;
  min-height: 0;
  border: none;
  border-radius: 0;
}
.map-topbar {
  position: absolute;
  z-index: 12;
  top: max(18px, env(safe-area-inset-top));
  right: 18px;
  left: 18px;
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr) 46px;
  align-items: center;
  gap: 10px;
}
.map-back,
.tune-button {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.96);
  color: #111;
  box-shadow: 0 14px 34px rgba(17, 17, 17, 0.16);
}
.map-back svg,
.tune-button svg,
.sheet-title button svg,
.venue-photo button svg {
  width: 22px;
  height: 22px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.search-pill {
  display: grid;
  justify-items: center;
  min-width: 0;
  min-height: 58px;
  padding: 8px 18px;
  border: 1px solid rgba(17, 17, 17, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.98);
  color: #111;
  box-shadow: 0 16px 40px rgba(17, 17, 17, 0.16);
}
.search-pill strong,
.search-pill span {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.search-pill strong {
  font-size: 16px;
  line-height: 1.15;
}
.search-pill span {
  color: #69716d;
  font-size: 13px;
  font-weight: 750;
}
.map-experience .map-filter-bar {
  top: calc(max(18px, env(safe-area-inset-top)) + 76px);
  right: 18px;
  left: 18px;
  display: flex;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}
.map-experience .map-filter-bar::-webkit-scrollbar {
  display: none;
}
.map-experience .map-filter-bar button {
  flex: 0 0 auto;
  min-width: 116px;
  padding: 0 18px;
}
.map-experience .locate-button {
  top: calc(max(18px, env(safe-area-inset-top)) + 138px);
  right: 18px;
}
.map-experience .map-message {
  right: 18px;
  bottom: 112px;
  left: 18px;
}
.map-experience .venue-sheet {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  gap: 12px;
  max-height: 58svh;
  margin: 0;
  padding: 12px 18px max(20px, env(safe-area-inset-bottom));
  overflow: auto;
  border: none;
  border-radius: 30px 30px 0 0;
  background: #fff;
  box-shadow: 0 -18px 52px rgba(17, 17, 17, 0.16);
  transition: max-height 0.22s ease;
}
.map-experience .venue-sheet:not(.expanded) {
  max-height: 104px;
  overflow: hidden;
}
.sheet-summary {
  display: grid;
  justify-items: center;
  gap: 5px;
  padding: 6px 0 10px;
  text-align: center;
}
.sheet-summary strong {
  font-size: 18px;
}
.sheet-summary span {
  max-width: 100%;
  overflow: hidden;
  color: #69716d;
  font-size: 13px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sheet-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}
.sheet-title p {
  margin: 0 0 4px;
  color: #69716d;
  font-size: 13px;
  font-weight: 850;
}
.sheet-title button {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 50%;
  background: #f0f2ef;
  color: #111;
}
.property-card {
  display: grid;
  gap: 10px;
}
.property-card .venue-photo {
  position: relative;
  height: min(31svh, 280px);
  min-height: 190px;
  overflow: hidden;
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(17, 17, 17, 0.08), rgba(17, 17, 17, 0)),
    radial-gradient(circle at 72% 24%, rgba(255, 255, 255, 0.8), transparent 0 42px, transparent 43px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.22) 50%, transparent 50%),
    linear-gradient(0deg, rgba(255, 255, 255, 0.2) 50%, transparent 50%),
    #7ed8cc;
  background-size: auto, auto, 56px 56px, 56px 56px, auto;
}
.property-card .venue-photo span {
  width: 72px;
  height: 72px;
  font-size: 30px;
}
.venue-photo button {
  position: absolute;
  top: 14px;
  right: 14px;
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  background: rgba(17, 17, 17, 0.22);
  color: #fff;
  backdrop-filter: blur(10px);
}
.venue-photo button svg {
  fill: rgba(255, 255, 255, 0.1);
}
.property-copy h3 {
  margin: 0 0 3px;
  font-size: 19px;
  line-height: 1.15;
}
.property-copy p {
  margin: 0;
  color: #69716d;
}

@keyframes spinBadge {
  to {
    transform: rotate(360deg);
  }
}
@keyframes flame-bounce {
  from {
    transform: translateY(2px) scale(0.96) rotate(-4deg);
  }
  to {
    transform: translateY(-3px) scale(1.04) rotate(4deg);
  }
}
@keyframes celebration-pop {
  0% {
    opacity: 0;
    transform: translateY(28px) scale(0.72);
  }
  62% {
    opacity: 1;
    transform: translateY(-8px) scale(1.04);
  }
  100% {
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 430px) {
  .activity-page {
    padding: 0 10px 28px;
  }
  .activity-home {
    padding-bottom: 104px;
  }
  .start-workout {
    right: 10px;
    left: 66px;
    min-height: 60px;
    font-size: 16px;
  }
  .map-canvas {
    height: 52svh;
    min-height: 340px;
    border-radius: 24px;
  }
  .map-canvas.fullscreen {
    height: auto;
    min-height: 0;
    border-radius: 0;
  }
  .map-topbar {
    right: 12px;
    left: 12px;
    grid-template-columns: 42px minmax(0, 1fr) 42px;
    gap: 8px;
  }
  .map-back,
  .tune-button {
    width: 42px;
    height: 42px;
  }
  .search-pill {
    min-height: 54px;
    padding: 7px 12px;
  }
  .map-experience .map-filter-bar {
    right: 12px;
    left: 12px;
  }
  .map-experience .locate-button {
    right: 12px;
  }
  .venue-sheet {
    margin-right: 8px;
    margin-left: 8px;
  }
  .map-experience .venue-sheet {
    right: 0;
    left: 0;
    max-height: 60svh;
    margin: 0;
    padding-right: 14px;
    padding-left: 14px;
  }
}
</style>
