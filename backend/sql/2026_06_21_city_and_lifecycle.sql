alter table venues
    add column if not exists city varchar(100) not null default 'Тараз';

create index if not exists idx_venues_city on venues(city);
create index if not exists idx_events_status_scheduled_at on events(status, scheduled_at);
