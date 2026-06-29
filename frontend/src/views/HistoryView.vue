<template>
  <section class="profile-page">
    <header class="topbar">
      <button class="back-button" type="button" aria-label="Назад">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18 9 12l6-6" /></svg>
      </button>
      <div>
        <h1>{{ userStore.profile?.name || "Профиль" }}</h1>
        <p>{{ totalGames }} игр</p>
      </div>
    </header>

    <div class="cover" aria-hidden="true"></div>

    <section class="profile-body">
      <div class="profile-actions">
        <button class="avatar" type="button" aria-label="Показать карточку игрока" @click="showCard">
          <span>{{ initials }}</span>
        </button>
      </div>

      <div class="profile-copy">
        <div class="name-line">
          <h2>{{ userStore.profile?.name || "Игрок" }}</h2>
        </div>
        <p class="handle">@{{ handle }}</p>
        <p class="bio">{{ userStore.profile?.bio || "Готов к новым играм рядом с собой." }}</p>

        <div class="meta-row">
          <span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11Z" /><path d="M12 10.5h.01" /></svg>
            {{ userStore.profile?.city || "Тараз" }}
          </span>
          <span>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 7V3M16 7V3M4 9h16M6 5h12a2 2 0 0 1 2 2v13H4V7a2 2 0 0 1 2-2Z" /></svg>
            Сегодня
          </span>
        </div>

        <button class="social-proof" type="button" aria-label="Показать статистику" @click="showStats">
          <span><strong>{{ publicationCount }}</strong> публикаций</span>
          <span><strong>{{ upcomingCount }}</strong> игр</span>
          <span><strong>{{ favoriteCount }}</strong> сохранено</span>
        </button>
      </div>

      <div
        class="showcase"
        @touchstart.passive="onTouchStart"
        @touchend.passive="onTouchEnd"
      >
        <div class="showcase-tabs" aria-label="Разделы профиля">
          <button :class="{ active: panel === 'card' }" type="button" @click="panel = 'card'">Карточка</button>
          <button :class="{ active: panel === 'stats' }" type="button" @click="panel = 'stats'">Статистика</button>
        </div>

        <div class="panels" :class="{ statsActive: panel === 'stats' }">
          <div class="panel card-panel">
            <button
              class="player-card-shell"
              type="button"
              :class="{ flipped: cardFlipped }"
              aria-label="Перевернуть карточку игрока"
              @click="cardFlipped = !cardFlipped"
            >
              <span class="card-face card-front">
                <span class="card-chip" aria-hidden="true"></span>
                <span class="card-emblem" aria-hidden="true">
                  <span>DS</span>
                </span>
                <span class="card-footer">
                  <span class="card-kind">player</span>
                  <span class="card-circles" aria-hidden="true">
                    <span></span>
                    <span></span>
                  </span>
                </span>
              </span>

              <span class="card-face card-back">
                <span class="card-strip" aria-hidden="true"></span>
                <span class="card-back-copy">
                  <strong>{{ userStore.profile?.name || "Игрок" }}</strong>
                  <small>{{ userStore.profile?.city || "Тараз" }}</small>
                </span>
                <span class="card-back-stats">
                  <span><strong>{{ totalGames }}</strong><small>игр</small></span>
                  <span><strong>{{ favoriteCount }}</strong><small>полей</small></span>
                  <span><strong>1000</strong><small>уровень</small></span>
                </span>
              </span>
            </button>
          </div>

          <div class="panel stats-panel">
            <div class="slot-tabs" aria-label="Слоты профиля">
              <button :class="{ active: tab === 'my' }" aria-label="Мои публикации" @click="tab = 'my'">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z" /></svg>
              </button>
              <button :class="{ active: tab === 'pending' }" aria-label="Ожидание" @click="tab = 'pending'">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
              </button>
              <button :class="{ active: tab === 'upcoming' }" aria-label="Предстоящие" @click="tab = 'upcoming'">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3v4M17 3v4M4 9h16M6 5h12a2 2 0 0 1 2 2v12H4V7a2 2 0 0 1 2-2Z" /></svg>
              </button>
              <button :class="{ active: tab === 'favorites' }" aria-label="Избранное" @click="tab = 'favorites'">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4h10a1 1 0 0 1 1 1v16l-6-3.5L6 21V5a1 1 0 0 1 1-1Z" /></svg>
              </button>
            </div>
            <div class="slot-content">
              <MyPublicationsTab v-show="tab === 'my'" @count="publicationCount = $event" />
              <PendingTab v-show="tab === 'pending'" @count="pendingCount = $event" />
              <UpcomingTab v-show="tab === 'upcoming'" @count="upcomingCount = $event" />
              <FavoritesTab v-show="tab === 'favorites'" @count="favoriteCount = $event" />
            </div>
          </div>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, ref } from "vue";
import MyPublicationsTab from "../components/history/MyPublicationsTab.vue";
import PendingTab from "../components/history/PendingTab.vue";
import UpcomingTab from "../components/history/UpcomingTab.vue";
import FavoritesTab from "../components/history/FavoritesTab.vue";
import { useUserStore } from "../stores/user";

const tab = ref("my");
const publicationCount = ref(0);
const pendingCount = ref(0);
const upcomingCount = ref(0);
const favoriteCount = ref(0);
const panel = ref("card");
const cardFlipped = ref(false);
const touchStartX = ref(null);
const userStore = useUserStore();

const totalGames = computed(() => publicationCount.value + upcomingCount.value);

const handle = computed(() => {
  const name = userStore.profile?.name || "user";
  return name.toLowerCase().replace(/[^a-zа-я0-9]+/gi, "").slice(0, 18) || "user";
});

const initials = computed(() => {
  const name = userStore.profile?.name || "DS";
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
});

function showCard() {
  panel.value = "card";
}

function showStats() {
  panel.value = "stats";
}

function onTouchStart(event) {
  touchStartX.value = event.changedTouches[0]?.clientX ?? null;
}

function onTouchEnd(event) {
  if (touchStartX.value === null) return;
  const endX = event.changedTouches[0]?.clientX ?? touchStartX.value;
  const delta = endX - touchStartX.value;
  touchStartX.value = null;
  if (Math.abs(delta) < 36) return;
  panel.value = delta < 0 ? "stats" : "card";
}
</script>

<style scoped>
.profile-page {
  min-height: 100svh;
  background: #fff;
  color: var(--text-main);
}
.topbar {
  position: sticky;
  z-index: 20;
  top: 0;
  display: flex;
  align-items: center;
  gap: 18px;
  max-width: 720px;
  min-height: 72px;
  margin: 0 auto;
  padding: 8px 18px;
  border-bottom: 1px solid var(--line-soft);
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(14px);
}
.back-button {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: #1d9bf0;
}
.back-button svg,
.meta-row svg {
  width: 21px;
  height: 21px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.topbar h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
  line-height: 1.05;
}
.topbar p {
  margin: 3px 0 0;
  color: #536471;
  font-size: 14px;
  line-height: 1;
}
.cover {
  position: relative;
  max-width: 720px;
  height: 242px;
  margin: 0 auto;
  overflow: hidden;
  background: #7ed8cc;
}
.profile-body {
  max-width: 720px;
  margin: 0 auto;
  border-right: 1px solid var(--line-soft);
  border-left: 1px solid var(--line-soft);
  background: #fff;
}
.profile-actions {
  position: relative;
  min-height: 84px;
  padding: 0 18px;
}
.avatar {
  display: grid;
  place-items: center;
  width: 156px;
  height: 156px;
  margin-top: -78px;
  padding: 5px;
  border: none;
  border-radius: 50%;
  background: #fff;
  color: var(--text-main);
}
.avatar span {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #7ed8cc;
  color: var(--text-main);
  font-size: 42px;
  font-weight: 900;
}
.profile-copy {
  padding: 0 18px 0;
}
.name-line {
  display: flex;
  align-items: center;
  gap: 7px;
}
.name-line h2 {
  margin: 0;
  overflow: hidden;
  color: var(--text-main);
  font-size: 27px;
  font-weight: 900;
  line-height: 1.05;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.handle {
  margin: 4px 0 0;
  color: #536471;
  font-size: 17px;
  line-height: 1.2;
}
.bio {
  margin: 12px 0 0;
  color: #0f1419;
  font-size: 17px;
  line-height: 1.35;
}
.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 18px;
  color: #536471;
  font-size: 16px;
}
.meta-row span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.social-proof {
  display: flex;
  flex-wrap: wrap;
  gap: 22px;
  margin: 18px 0 0;
  padding: 0;
  border: none;
  background: transparent;
  color: #536471;
  font-size: 16px;
  text-align: left;
}
.social-proof strong {
  color: #0f1419;
  font-weight: 900;
}
.showcase {
  margin-top: 28px;
  overflow: hidden;
}
.showcase-tabs {
  display: flex;
  width: 100%;
  border-bottom: 1px solid var(--line-soft);
  background: #fff;
}
.showcase-tabs button {
  position: relative;
  flex: 1;
  min-height: 58px;
  border: none;
  background: transparent;
  color: #536471;
  font-size: 16px;
  font-weight: 900;
}
.showcase-tabs button.active {
  color: #0f1419;
}
.showcase-tabs button.active::after {
  content: "";
  position: absolute;
  right: 35%;
  bottom: 0;
  left: 35%;
  height: 4px;
  border-radius: 999px;
  background: #1d9bf0;
}
.panels {
  display: flex;
  width: 200%;
  transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}
.panels.statsActive {
  transform: translateX(-50%);
}
.panel {
  display: grid;
  place-items: center;
  width: 50%;
  min-height: 420px;
  padding: 28px 18px 38px;
}
.stats-panel {
  align-content: start;
  gap: 12px;
}
.player-card-shell {
  position: relative;
  display: block;
  width: min(74vw, 300px);
  aspect-ratio: 0.68;
  border: none;
  background: transparent;
  color: #101820;
  cursor: pointer;
  perspective: 1000px;
  transform-style: preserve-3d;
  animation: card-float 4.8s ease-in-out infinite;
}
.player-card-shell::after {
  content: "";
  position: absolute;
  right: 10%;
  bottom: -20px;
  left: 10%;
  height: 28px;
  border-radius: 50%;
  background: rgba(15, 20, 25, 0.16);
  filter: blur(14px);
  animation: card-shadow 4.8s ease-in-out infinite;
}
.card-face {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: 22px;
  background: #ff806d;
  box-shadow: 0 16px 34px rgba(15, 20, 25, 0.15);
  backface-visibility: hidden;
  transform-style: preserve-3d;
  transition: transform 0.68s cubic-bezier(0.22, 1, 0.36, 1);
}
.card-front {
  transform: rotateY(0deg);
}
.card-back {
  display: grid;
  align-content: end;
  gap: 22px;
  padding: 28px 24px;
  background: #101820;
  color: #fff;
  transform: rotateY(180deg);
}
.player-card-shell.flipped .card-front {
  transform: rotateY(-180deg);
}
.player-card-shell.flipped .card-back {
  transform: rotateY(0deg);
}
.card-chip {
  position: absolute;
  top: 56px;
  left: 50%;
  width: 54px;
  height: 42px;
  border: 2px solid rgba(15, 20, 25, 0.46);
  border-radius: 8px;
  background:
    linear-gradient(90deg, transparent 33%, rgba(15, 20, 25, 0.36) 33% 37%, transparent 37% 63%, rgba(15, 20, 25, 0.36) 63% 67%, transparent 67%),
    linear-gradient(0deg, transparent 47%, rgba(15, 20, 25, 0.36) 47% 53%, transparent 53%),
    #f4edb9;
  transform: translateX(-50%);
}
.card-emblem {
  position: absolute;
  top: 150px;
  left: 50%;
  display: grid;
  place-items: center;
  width: 132px;
  height: 118px;
  transform: translateX(-50%);
}
.card-emblem::before {
  content: "";
  position: absolute;
  inset: 0 14px;
  border: 4px solid rgba(255, 255, 255, 0.72);
  clip-path: polygon(50% 0, 100% 100%, 0 100%);
}
.card-emblem span {
  position: relative;
  z-index: 1;
  font-size: 42px;
  font-style: italic;
  font-weight: 950;
  letter-spacing: -0.08em;
}
.card-footer {
  position: absolute;
  right: 24px;
  bottom: 22px;
  left: 24px;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: end;
}
.card-kind {
  color: #fff;
  font-size: 27px;
  font-weight: 900;
  letter-spacing: 0.02em;
}
.card-circles {
  position: relative;
  width: 86px;
  height: 50px;
}
.card-circles span {
  position: absolute;
  top: 5px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  opacity: 0.86;
}
.card-circles span:first-child {
  left: 2px;
  background: #ec001b;
}
.card-circles span:last-child {
  right: 2px;
  background: #ffb226;
}
.card-strip {
  position: absolute;
  top: 42px;
  right: 0;
  left: 0;
  height: 58px;
  background: rgba(255, 255, 255, 0.16);
}
.card-back-copy {
  display: grid;
  gap: 5px;
  text-align: left;
}
.card-back-copy strong {
  font-size: 28px;
  font-weight: 900;
  line-height: 1;
}
.card-back-copy small {
  color: rgba(255, 255, 255, 0.66);
  font-size: 15px;
  font-weight: 800;
}
.card-back-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.24);
}
.card-back-stats span,
.card-back-stats strong,
.card-back-stats small {
  display: block;
}
.card-back-stats strong {
  font-size: 20px;
  font-weight: 900;
}
.card-back-stats small {
  margin-top: 3px;
  color: rgba(255, 255, 255, 0.66);
  font-size: 11px;
  font-weight: 800;
}
@keyframes card-float {
  0%,
  100% {
    transform: translateY(0) rotateZ(-0.8deg);
  }
  50% {
    transform: translateY(-12px) rotateZ(0.8deg);
  }
}
@keyframes card-shadow {
  0%,
  100% {
    opacity: 0.9;
    transform: scaleX(1);
  }
  50% {
    opacity: 0.55;
    transform: scaleX(0.82);
  }
}
.slot-tabs {
  display: flex;
  width: 100%;
  border-top: 1px solid var(--line-soft);
  border-bottom: 1px solid var(--line-soft);
  background: #fff;
}
.slot-tabs button {
  position: relative;
  display: grid;
  place-items: center;
  flex: 1;
  min-height: 58px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #536471;
}
.slot-tabs button.active {
  border-bottom-color: #1d9bf0;
  color: #0f1419;
}
.slot-tabs svg {
  width: 27px;
  height: 27px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.slot-tabs button:first-child svg {
  fill: currentColor;
  stroke-width: 1.2;
}
.slot-content {
  width: 100%;
  min-height: 180px;
  overflow: hidden;
  border-bottom: 1px solid var(--line-soft);
  background: #fff;
}
.slot-content :deep(.list) {
  padding: 12px 18px;
}
.slot-content :deep(.empty) {
  padding: 28px 14px;
}

@media (max-width: 430px) {
  .topbar {
    min-height: 62px;
    padding: 7px 12px;
  }
  .cover {
    height: 176px;
  }
  .profile-body {
    border-right: none;
    border-left: none;
  }
  .avatar {
    width: 118px;
    height: 118px;
    margin-top: -59px;
  }
  .avatar span {
    font-size: 32px;
  }
  .profile-actions {
    min-height: 68px;
    padding: 0 14px;
  }
  .profile-copy {
    padding: 0 14px;
  }
  .name-line h2 {
    font-size: 23px;
  }
  .handle,
  .bio,
  .meta-row,
  .social-proof {
    font-size: 15px;
  }
  .panel {
    min-height: 380px;
    padding: 24px 14px 34px;
  }
  .player-card-shell {
    width: min(76vw, 260px);
  }
  .card-front .card-chip {
    top: 45px;
  }
  .card-front .card-emblem {
    top: 125px;
  }
  .card-kind {
    font-size: 24px;
  }
  .card-back-copy strong {
    font-size: 24px;
  }
}
</style>
