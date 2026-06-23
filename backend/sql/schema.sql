-- Схема для Supabase (PostgreSQL). Соответствует моделям SQLAlchemy
-- в backend/app/models. Можно выполнить целиком в SQL Editor Supabase,
-- либо использовать SQLAlchemy Base.metadata.create_all для дев-окружения.

create type venue_status as enum ('free', 'occupied');
create type event_status as enum ('open', 'full', 'cancelled', 'completed');
create type application_status as enum ('pending', 'accepted', 'declined', 'cancelled');

create table users (
    id bigserial primary key,
    telegram_id bigint unique not null,
    name varchar(100) not null,
    age int,
    photos text[] default '{}',
    city varchar(100) default 'Тараз',
    bio text,
    created_at timestamptz default now()
);

create table venues (
    id bigserial primary key,
    name varchar(200) not null,
    sport_type varchar(100),
    city varchar(100) not null default 'Тараз',
    latitude double precision not null,
    longitude double precision not null,
    is_paid boolean default false,
    price numeric(10, 2),
    status venue_status default 'free',
    address varchar(300)
);

create table events (
    id bigserial primary key,
    captain_id bigint references users(id) on delete cascade,
    venue_id bigint references venues(id),
    sport_type varchar(100),
    group_link varchar(300),
    scheduled_at timestamptz,
    price numeric(10, 2),
    slots_total int not null,
    slots_available int not null,
    status event_status default 'open',
    reminder_sent boolean default false,
    created_at timestamptz default now()
);

create table event_applications (
    id bigserial primary key,
    event_id bigint references events(id) on delete cascade,
    user_id bigint references users(id) on delete cascade,
    status application_status default 'pending',
    created_at timestamptz default now(),
    responded_at timestamptz,
    unique (event_id, user_id)
);

create table event_favorites (
    id bigserial primary key,
    event_id bigint references events(id) on delete cascade,
    user_id bigint references users(id) on delete cascade,
    created_at timestamptz default now(),
    unique (event_id, user_id)
);

create index idx_events_status on events(status);
create index idx_events_captain on events(captain_id);
create index idx_applications_event on event_applications(event_id);
create index idx_applications_user on event_applications(user_id);
create index idx_events_feed on events(status, id desc);
create index idx_events_status_scheduled_at on events(status, scheduled_at);
create index idx_applications_user_event on event_applications(user_id, event_id);
create index idx_venues_city on venues(city);
create index idx_favorites_user_created on event_favorites(user_id, created_at desc);
create index idx_favorites_event on event_favorites(event_id);
