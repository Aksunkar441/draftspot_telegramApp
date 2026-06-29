import client from "./client";

export const createCheckin = (payload) => client.post("/checkins", payload).then((r) => r.data);
