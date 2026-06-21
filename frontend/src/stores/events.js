import { defineStore } from "pinia";
import { getFeed, joinEvent } from "../api/events";

const PAGE_SIZE = 10;
const PREFETCH_THRESHOLD = 3;

export const useEventsStore = defineStore("events", {
  state: () => ({
    feed: [],
    cursor: 0,
    nextCursor: null,
    loading: false,
    exhausted: false,
    error: null,
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
        const page = await getFeed({ cursor: this.nextCursor, limit: PAGE_SIZE });
        this.feed.push(...page.items);
        this.nextCursor = page.next_cursor;
        this.exhausted = page.next_cursor === null;
      } catch (error) {
        this.error = error;
        throw error;
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
      this.cursor += 1;
      await this.ensureBuffered();
    },
    async join() {
      const event = this.current;
      if (!event) return;
      await joinEvent(event.id);
      this.cursor += 1;
      await this.ensureBuffered();
    },
  },
});
