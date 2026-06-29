create table if not exists venue_checkins (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    venue_id bigint references venues(id) on delete cascade,
    checked_date date not null,
    latitude double precision not null,
    longitude double precision not null,
    distance_meters int not null,
    created_at timestamptz default now(),
    constraint uq_venue_checkin_daily unique (user_id, venue_id, checked_date)
);

create index if not exists idx_checkins_user_date
    on venue_checkins(user_id, checked_date desc);

create index if not exists idx_checkins_venue_date
    on venue_checkins(venue_id, checked_date desc);
