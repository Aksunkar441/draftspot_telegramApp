import { defineStore } from "pinia";
import { getFeed, joinEvent } from "../api/events";
import { addFavorite } from "../api/favorites";

const PAGE_SIZE = 10;
const PREFETCH_THRESHOLD = 3;
const SAVED_KEY = "draftspot:saved-events";
const SKIPPED_KEY = "draftspot:skipped-events";
export const DEMO_EVENTS = [
  {
    id: -101,
    sport_type: "Футбол 5x5",
    scheduled_at: new Date(Date.now() + 1000 * 60 * 60 * 5).toISOString(),
    price: 0,
    slots_total: 10,
    slots_available: 4,
    demo: true,
    venue: {
      id: -1,
      name: "Дворовая площадка Алатау",
      sport_type: "Футбол",
      city: "Тараз",
      latitude: 42.8876,
      longitude: 71.3456,
      is_paid: false,
      price: 0,
      status: "free",
      address: "мкр. Алатау, возле д. 15",
    },
  },
  {
    id: -102,
    sport_type: "Баскетбол",
    scheduled_at: new Date(Date.now() + 1000 * 60 * 60 * 27).toISOString(),
    price: 3000,
    slots_total: 8,
    slots_available: 3,
    demo: true,
    venue: {
      id: -2,
      name: "Спорткомплекс Олимпик",
      sport_type: "Баскетбол",
      city: "Тараз",
      latitude: 42.9055,
      longitude: 71.3789,
      is_paid: true,
      price: 3000,
      status: "free",
      address: "мкр. Самал, 12",
    },
  },
];

export function isLocalDemoMode() {
  return import.meta.env.DEV && !window.Telegram?.WebApp?.initData;
}

function readStoredIds(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || "[]");
  } catch {
    return [];
  }
}

function writeStoredIds(key, ids) {
  localStorage.setItem(key, JSON.stringify([...new Set(ids)]));
}

export const useEventsStore = defineStore("events", {
  state: () => ({
    feed: [],
    cursor: 0,
    nextCursor: null,
    loading: false,
    actionLoading: false,
    exhausted: false,
    error: null,
    actionError: null,
    savedIds: readStoredIds(SAVED_KEY),
    skippedIds: readStoredIds(SKIPPED_KEY),
  }),
  getters: {
    current(state) {
      return state.feed[state.cursor] ?? null;
    },
    hasBufferedItems(state) {
      return state.cursor < state.feed.length;
    },
  },
  actions: {
    isIgnored(id) {
      return this.savedIds.includes(id) || this.skippedIds.includes(id);
    },
    async loadFeed({ reset = false } = {}) {
      if (this.loading) return;
      if (!reset && this.exhausted) return;

      if (reset) {
        this.feed = [];
        this.cursor = 0;
        this.nextCursor = null;
        this.exhausted = false;
        this.error = null;
      }

      this.loading = true;
      try {
        let attempts = 0;
        while (attempts < 3 && !this.exhausted) {
          const page = await getFeed({ cursor: this.nextCursor, limit: PAGE_SIZE });
          const existingIds = new Set(this.feed.map((event) => event.id));
          const freshItems = page.items.filter(
            (event) => !existingIds.has(event.id) && !this.isIgnored(event.id)
          );
          this.feed.push(...freshItems);
          this.nextCursor = page.next_cursor;
          this.exhausted = page.next_cursor === null;
          attempts += 1;
          if (freshItems.length > 0 || this.exhausted) break;
        }
      } catch (error) {
        if (isLocalDemoMode()) {
          this.feed.push(...DEMO_EVENTS.filter((event) => !this.isIgnored(event.id)));
          this.nextCursor = null;
          this.exhausted = true;
          this.error = null;
        } else {
          this.error = error;
        }
      } finally {
        this.loading = false;
      }
    },
    async ensureBuffered() {
      const remaining = this.feed.length - this.cursor;
      if (remaining <= PREFETCH_THRESHOLD) {
        await this.loadFeed();
      }
    },
    async skip() {
      const event = this.current;
      if (event && !this.skippedIds.includes(event.id)) {
        this.skippedIds.push(event.id);
        writeStoredIds(SKIPPED_KEY, this.skippedIds);
      }
      this.cursor += 1;
      await this.ensureBuffered();
    },
    async favorite() {
      const event = this.current;
      if (!event) return;
      this.actionLoading = true;
      this.actionError = null;
      try {
        if (!event.demo) {
          await addFavorite(event.id);
        }
        if (!this.savedIds.includes(event.id)) {
          this.savedIds.push(event.id);
          writeStoredIds(SAVED_KEY, this.savedIds);
        }
        this.cursor += 1;
        await this.ensureBuffered();
      } catch (error) {
        this.actionError = error.response?.data?.detail ?? "Не удалось добавить в избранное";
      } finally {
        this.actionLoading = false;
      }
    },
    async join() {
      const event = this.current;
      if (!event) return;
      this.actionLoading = true;
      this.actionError = null;
      try {
        if (!event.demo) {
          await joinEvent(event.id);
        }
        this.cursor += 1;
        await this.ensureBuffered();
      } catch (error) {
        this.actionError = error.response?.data?.detail ?? "Не удалось отправить заявку";
      } finally {
        this.actionLoading = false;
      }
    },
  },
});
