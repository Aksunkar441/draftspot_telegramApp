import { defineStore } from "pinia";
import { getMe } from "../api/users";

export const useUserStore = defineStore("user", {
  state: () => ({
    profile: null,
    loaded: false,
  }),
  actions: {
    async load() {
      try {
        this.profile = await getMe();
      } catch (e) {
        this.profile = null;
      } finally {
        this.loaded = true;
      }
    },
  },
});
