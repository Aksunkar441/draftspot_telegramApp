import client from "./client";

export const getFeed = () => client.get("/events/feed").then((r) => r.data);
export const getMyEvents = () => client.get("/events/my").then((r) => r.data);
export const getEvent = (id) => client.get(`/events/${id}`).then((r) => r.data);
export const createEvent = (payload) => client.post("/events", payload).then((r) => r.data);
export const joinEvent = (id) => client.post(`/events/${id}/join`).then((r) => r.data);
export const deleteEvent = (id) => client.delete(`/events/${id}`).then((r) => r.data);
export const getVenues = () => client.get("/venues").then((r) => r.data);
