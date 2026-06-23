<template>
  <section class="map-card" :aria-label="`Карта: ${venue.name}`">
    <div class="map-surface">
      <div class="grid-lines"></div>
      <div class="route route-main"></div>
      <div class="route route-side"></div>
      <div class="marker">
        <span></span>
      </div>
      <div class="map-label top">{{ venue.city || "Город" }}</div>
      <div class="map-label bottom">{{ coordinateLabel }}</div>
    </div>

    <div class="map-meta">
      <div>
        <p class="eyebrow">Локация</p>
        <h3>{{ venue.name }}</h3>
        <p>{{ venue.address || "Адрес уточняется" }}</p>
      </div>
      <div class="links">
        <a :href="googleUrl" target="_blank" rel="noreferrer">Google</a>
        <a :href="twoGisUrl" target="_blank" rel="noreferrer">2GIS</a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  venue: { type: Object, required: true },
});

const coordinateLabel = computed(() => {
  const lat = Number(props.venue.latitude);
  const lng = Number(props.venue.longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return "Координаты уточняются";
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
});

const googleUrl = computed(() => {
  const lat = props.venue.latitude;
  const lng = props.venue.longitude;
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
});

const twoGisUrl = computed(() => {
  const lat = props.venue.latitude;
  const lng = props.venue.longitude;
  return `https://2gis.kz/search/${lat}%2C${lng}`;
});
</script>

<style scoped>
.map-card {
  display: grid;
  gap: 14px;
  height: 100%;
  min-height: 0;
}
.map-surface {
  position: relative;
  overflow: hidden;
  min-height: 310px;
  border: 1px solid var(--line-soft);
  border-radius: 22px;
  background:
    radial-gradient(circle at 66% 42%, rgba(17, 17, 17, 0.08), transparent 0 8px, transparent 9px),
    linear-gradient(135deg, #f5f5f3 0%, #deded9 100%);
  color: var(--black);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
}
.grid-lines {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(0, 0, 0, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(0, 0, 0, 0.08) 1px, transparent 1px);
  background-size: 44px 44px;
  opacity: 0.42;
}
.route {
  position: absolute;
  border-radius: 999px;
  background: var(--black);
  opacity: 0.82;
}
.route-main {
  left: -12%;
  top: 53%;
  width: 128%;
  height: 16px;
  transform: rotate(-17deg);
}
.route-side {
  left: 50%;
  top: -6%;
  width: 15px;
  height: 112%;
  transform: rotate(22deg);
}
.marker {
  position: absolute;
  left: 58%;
  top: 44%;
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border: 2px solid var(--black);
  border-radius: 50%;
  background: rgba(248, 247, 242, 0.86);
  transform: translate(-50%, -50%);
  box-shadow: 0 18px 30px rgba(0, 0, 0, 0.24);
}
.marker span {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--black);
}
.map-label {
  position: absolute;
  max-width: calc(100% - 32px);
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(17, 17, 17, 0.9);
  color: #fff;
  font-size: 12px;
  font-weight: 800;
}
.map-label.top {
  top: 14px;
  left: 14px;
}
.map-label.bottom {
  right: 14px;
  bottom: 14px;
}
.map-meta {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
}
.eyebrow {
  margin: 0 0 5px;
  color: var(--text-faint);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
h3 {
  margin: 0 0 6px;
  color: var(--text-main);
  font-size: 20px;
  line-height: 1.08;
}
p {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.35;
}
.links {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.links a {
  padding: 10px 12px;
  border-radius: 999px;
  border: 1px solid var(--line-soft);
  background: #fff;
  color: var(--text-main);
  font-size: 12px;
  font-weight: 900;
  text-decoration: none;
}

@media (max-width: 430px) {
  .map-surface {
    min-height: 250px;
  }
  .map-meta {
    display: grid;
  }
  .links {
    width: 100%;
  }
  .links a {
    flex: 1;
    text-align: center;
  }
}
</style>
