import client from "./client";

export const getPending = () => client.get("/applications/pending").then((r) => r.data);
export const getUpcoming = () => client.get("/applications/upcoming").then((r) => r.data);
export const acceptApplication = (id) => client.post(`/applications/${id}/accept`).then((r) => r.data);
export const declineApplication = (id) => client.post(`/applications/${id}/decline`).then((r) => r.data);
export const cancelApplication = (id) => client.post(`/applications/${id}/cancel`).then((r) => r.data);
export const kickPlayer = (id) => client.post(`/applications/${id}/kick`).then((r) => r.data);
