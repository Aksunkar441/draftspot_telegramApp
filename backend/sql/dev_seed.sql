-- Development seed for Supabase dev/staging only.
-- Safe to rerun: it removes previously seeded rows by marker and recreates them.

begin;

update users
set city = 'Тараз'
where city is not null
  and lower(trim(city)) in ('тараз', 'taraz');

delete from event_favorites
where event_id in (select id from events where group_link = 'https://t.me/draftspot_dev_seed')
   or user_id in (select id from users where telegram_id in (900000001, 900000002, 900000003));

delete from event_applications
where event_id in (select id from events where group_link = 'https://t.me/draftspot_dev_seed')
   or user_id in (select id from users where telegram_id in (900000001, 900000002, 900000003));

delete from events
where group_link = 'https://t.me/draftspot_dev_seed'
   or captain_id in (select id from users where telegram_id in (900000001, 900000002, 900000003));

delete from venues
where address like 'DEV seed:%';

delete from users
where telegram_id in (900000001, 900000002, 900000003);

with users_seed as (
    insert into users (telegram_id, name, age, city, bio)
    values
        (900000001, 'Аксункар Dev', 24, 'Тараз', 'Тестовый капитан для dev-среды.'),
        (900000002, 'Галым Dev', 25, 'Тараз', 'Любит футбол и быстрые сборы.'),
        (900000003, 'Данияр Dev', 23, 'Тараз', 'Тестовый игрок для заявок.')
    returning id, telegram_id
),
venues_seed as (
    insert into venues (name, sport_type, city, latitude, longitude, is_paid, price, status, address)
    values
        ('Центральное поле Dev', 'Футбол', 'Тараз', 42.900000, 71.366700, false, 0, 'free', 'DEV seed: Центральный парк, Тараз'),
        ('Арена 3x3 Dev', 'Баскетбол', 'Тараз', 42.895800, 71.374900, false, 0, 'free', 'DEV seed: ул. Толе би, Тараз'),
        ('Теннисный корт Dev', 'Теннис', 'Тараз', 42.904200, 71.352500, true, 2500, 'free', 'DEV seed: спорткомплекс, Тараз')
    returning id, name
),
events_seed as (
    insert into events (
        captain_id,
        venue_id,
        sport_type,
        group_link,
        scheduled_at,
        price,
        slots_total,
        slots_available,
        status
    )
    values
        (
            (select id from users_seed where telegram_id = 900000002),
            (select id from venues_seed where name = 'Центральное поле Dev'),
            'Футбол 5x5',
            'https://t.me/draftspot_dev_seed',
            now() + interval '1 day 3 hours',
            null,
            10,
            7,
            'open'
        ),
        (
            (select id from users_seed where telegram_id = 900000003),
            (select id from venues_seed where name = 'Арена 3x3 Dev'),
            'Баскетбол 3x3',
            'https://t.me/draftspot_dev_seed',
            now() + interval '2 days 1 hour',
            null,
            6,
            5,
            'open'
        ),
        (
            (select id from users_seed where telegram_id = 900000001),
            (select id from venues_seed where name = 'Теннисный корт Dev'),
            'Теннис парами',
            'https://t.me/draftspot_dev_seed',
            now() + interval '3 days',
            2500,
            4,
            3,
            'open'
        ),
        (
            (select id from users_seed where telegram_id = 900000002),
            (select id from venues_seed where name = 'Центральное поле Dev'),
            'Футбол завершенный',
            'https://t.me/draftspot_dev_seed',
            now() - interval '1 day',
            null,
            8,
            0,
            'completed'
        )
    returning id, sport_type
)
insert into event_applications (event_id, user_id, status, responded_at)
values
    (
        (select id from events_seed where sport_type = 'Футбол 5x5'),
        (select id from users_seed where telegram_id = 900000001),
        'pending',
        null
    ),
    (
        (select id from events_seed where sport_type = 'Баскетбол 3x3'),
        (select id from users_seed where telegram_id = 900000001),
        'accepted',
        now()
    );

insert into event_favorites (event_id, user_id)
select e.id, u.id
from events e
cross join users u
where e.group_link = 'https://t.me/draftspot_dev_seed'
  and u.telegram_id = 900000001
  and e.sport_type in ('Футбол 5x5', 'Футбол завершенный');

commit;
