import { createRouter, createWebHistory } from "vue-router";
import FeedView from "../views/FeedView.vue";
import HistoryView from "../views/HistoryView.vue";
import EventDetailView from "../views/EventDetailView.vue";
import CreateEventView from "../views/CreateEventView.vue";

const routes = [
  { path: "/", name: "feed", component: FeedView },
  { path: "/history", name: "history", component: HistoryView },
  { path: "/events/:id", name: "event-detail", component: EventDetailView, props: true },
  { path: "/create", name: "create-event", component: CreateEventView },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
