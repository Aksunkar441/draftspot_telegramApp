<template>
  <section class="profile-page">
    <header class="profile-header">
      <div class="profile-topline">
        <strong>{{ userStore.profile?.name || "Профиль" }}</strong>
        <span>{{ userStore.profile?.city || "Тараз" }}</span>
      </div>

      <div class="profile-main">
        <div class="avatar">
          <span>{{ initials }}</span>
        </div>
        <div class="stats">
          <div>
            <strong>{{ publicationCount }}</strong>
            <span>Посты</span>
          </div>
          <div>
            <strong>{{ pendingCount }}</strong>
            <span>Ожидание</span>
          </div>
          <div>
            <strong>{{ upcomingCount }}</strong>
            <span>Игры</span>
          </div>
          <div>
            <strong>{{ favoriteCount }}</strong>
            <span>Избранное</span>
          </div>
        </div>
      </div>

      <div class="bio">
        <strong>{{ userStore.profile?.name || "Игрок" }}</strong>
        <p>{{ userStore.profile?.bio || "Готов к новым играм рядом с собой." }}</p>
      </div>

      <div class="tabs">
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
    </header>

    <div class="profile-content">
      <MyPublicationsTab v-if="tab === 'my'" @count="publicationCount = $event" />
      <PendingTab v-else-if="tab === 'pending'" @count="pendingCount = $event" />
      <UpcomingTab v-else-if="tab === 'upcoming'" @count="upcomingCount = $event" />
      <FavoritesTab v-else @count="favoriteCount = $event" />
    </div>
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
const userStore = useUserStore();

const initials = computed(() => {
  const name = userStore.profile?.name || "DS";
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
});
</script>

<style scoped>
.profile-page {
  min-height: 100svh;
  background: var(--surface-muted);
  color: var(--text-main);
}
.profile-header {
  position: sticky;
  z-index: 8;
  top: 0;
  padding: 18px 16px 0;
  border-bottom: 1px solid var(--line-soft);
  background: rgba(244, 244, 242, 0.92);
  backdrop-filter: blur(18px);
}
.profile-topline {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  font-size: 18px;
}
.profile-topline strong {
  max-width: 58vw;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.profile-topline span {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 800;
}
.profile-main {
  display: grid;
  grid-template-columns: 94px 1fr;
  gap: 18px;
  align-items: center;
}
.avatar {
  display: grid;
  place-items: center;
  width: 92px;
  height: 92px;
  padding: 3px;
  border: 1px solid var(--line-soft);
  border-radius: 50%;
  background: #fff;
  box-shadow: var(--shadow-soft);
}
.avatar span {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  border: 1px solid var(--line-soft);
  border-radius: 50%;
  background: var(--surface-soft);
  color: var(--text-main);
  font-size: 24px;
  font-weight: 950;
}
.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  text-align: center;
}
.stats strong,
.stats span {
  display: block;
}
.stats strong {
  font-size: 18px;
}
.stats span {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.1;
}
.bio {
  margin-top: 14px;
}
.bio strong {
  display: block;
  font-size: 14px;
}
.bio p {
  margin: 3px 0 0;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.35;
}
.tabs {
  display: flex;
  margin: 18px -16px 0;
  border-top: 1px solid var(--line-soft);
  background: #fff;
}
.tabs button {
  flex: 1;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 11px 0 9px;
  background: transparent;
  color: var(--text-faint);
}
.tabs button.active {
  border-bottom-color: var(--black);
  color: var(--text-main);
}
.tabs svg {
  width: 25px;
  height: 25px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.tabs button:first-child svg {
  fill: currentColor;
  stroke-width: 1.2;
}
.profile-content {
  padding: 14px 0 24px;
}

@media (max-width: 430px) {
  .profile-header {
    padding: 16px 12px 0;
  }
  .profile-main {
    grid-template-columns: 80px 1fr;
    gap: 12px;
  }
  .avatar {
    width: 78px;
    height: 78px;
  }
}
</style>
