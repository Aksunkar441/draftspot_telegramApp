import client from "./client";

export const getFavorites = () => client.get("/favorites").then((r) => r.data);
export const addFavorite = (eventId) => client.post(`/favorites/${eventId}`).then((r) => r.data);
export const removeFavorite = (eventId) => client.delete(`/favorites/${eventId}`).then((r) => r.data);
