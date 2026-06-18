import { defineStore } from "pinia";
import { getFeed, joinEvent } from "../api/events";

export const useEventsStore = defineStore("events", {
  state: () => ({
    feed: [],
    cursor: 0,
  }),
  getters: {
    current(state) {
      return state.feed[state.cursor] ?? null;
    },
  },
  actions: {
    async loadFeed() {
      this.feed = await getFeed();
      this.cursor = 0;
    },
    skip() {
      this.cursor += 1;
    },
    async join() {
      const event = this.current;
      if (!event) return;
      await joinEvent(event.id);
      this.cursor += 1;
    },
  },
});
