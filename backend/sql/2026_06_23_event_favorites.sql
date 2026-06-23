create table if not exists event_favorites (
    id bigserial primary key,
    event_id bigint references events(id) on delete cascade,
    user_id bigint references users(id) on delete cascade,
    created_at timestamptz default now(),
    unique (event_id, user_id)
);

create index if not exists idx_favorites_user_created
    on event_favorites(user_id, created_at desc);

create index if not exists idx_favorites_event
    on event_favorites(event_id);
