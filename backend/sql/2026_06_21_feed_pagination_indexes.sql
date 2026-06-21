create index if not exists idx_events_feed on events(status, id desc);
create index if not exists idx_applications_user_event on event_applications(user_id, event_id);
