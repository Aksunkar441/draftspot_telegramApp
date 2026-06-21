# Sport Meetup — бот + Mini App для сборов на игру

Стек: **Vue.js 3 (Mini App)** + **FastAPI** + **Aiogram 3** + **PostgreSQL / Supabase**.

## Структура проекта

```
backend/
  app/
    main.py              — точка входа FastAPI, регистрация роутов и вебхука бота
    config.py             — настройки из .env
    database.py            — async-движок SQLAlchemy, сессии
    core/security.py        — проверка подписи Telegram initData
    models/                — SQLAlchemy-модели (User, Venue, Event, EventApplication)
    schemas/               — Pydantic-схемы запросов/ответов
    api/
      deps.py               — получение текущего пользователя из initData
      routes/                — users, venues, events, applications
    services/
      event_service.py        — атомарное принятие заявки (защита от гонки)
      notification_service.py  — отправка сообщений через бота
      reminder_service.py       — старый отключённый прототип напоминаний
    bot/
      bot_instance.py           — экземпляр Bot/Dispatcher
      states.py                  — FSM-состояния регистрации
      keyboards.py                 — инлайн-клавиатуры
      handlers/
        start.py                   — /start, проверка регистрации
        registration.py             — FSM: имя → возраст → фото → описание
        captain_actions.py           — accept/decline прямо из чата
  sql/schema.sql            — DDL для Supabase (SQL Editor)
  requirements.txt
  .env.example

frontend/
  src/
    api/                — axios-клиент + обёртки над эндпоинтами
    stores/              — Pinia: профиль пользователя, лента событий
    router/                — vue-router
    views/
      FeedView.vue          — лента "присоединиться / смотреть дальше"
      EventDetailView.vue    — карточка сбора + управление заявками капитаном
      CreateEventView.vue     — публикация нового сбора
      HistoryView.vue           — три слота
    components/
      EventCard.vue
      history/
        MyPublicationsTab.vue
        PendingTab.vue
        UpcomingTab.vue
```

## Как это работает

**Регистрация** происходит в боте, а не в Mini App: `/start` → имя → возраст → город → одно или несколько фото (`file_id` Telegram, без загрузки на свой сервер) → описание (можно пропустить). Город сохраняется в `users.city` и используется для фильтрации площадок и ленты.

**Авторизация Mini App**: фронтенд на каждый запрос кладёт в заголовок `X-Telegram-Init-Data` значение `window.Telegram.WebApp.initData`. Backend проверяет HMAC-подпись этой строки секретом, производным от токена бота (`app/core/security.py`) — без этого любой человек мог бы прислать произвольный `telegram_id` и авторизоваться под чужим профилем.

**Лента** (`/api/events/feed`) отдаёт открытые события в городе пользователя, кроме тех, что создал сам пользователь или на которые он уже подавал заявку. Backend использует курсорную пагинацию (`limit`, `cursor`) и `LEFT JOIN ... IS NULL`, поэтому клиент не загружает все события одним тяжёлым массивом.

**Заявка на присоединение**: `POST /events/{id}/join` создаёт `EventApplication` со статусом `pending` и шлёт капитану сообщение в боте с кнопками «Принять / Отклонить» прямо в чате (плюс то же самое доступно из Mini App на странице события).

**Защита от гонки при принятии заявки** — самое важное место в бизнес-логике. Если у капитана осталось одно свободное место и он успевает нажать «Принять» на двух заявках почти одновременно, наивный код (прочитать `slots_available`, проверить > 0, потом записать -1) пропустит обе. Поэтому `event_service.accept_application` делает это одним SQL-запросом:

```sql
UPDATE events SET slots_available = slots_available - 1
WHERE id = :event_id AND slots_available > 0
RETURNING id, slots_available;
```

PostgreSQL блокирует строку на время выполнения запроса, поэтому при параллельных вызовах вторая транзакция either увидит уже `slots_available = 0` и не сможет списать место, либо встанет в очередь и получит актуальное значение. Если `RETURNING` ничего не вернул — мест не осталось, заявка не принимается, капитан получает 400.

**Три слота истории** реализованы как отдельные эндпоинты, а не как фильтрация одного списка на фронте, чтобы не тащить на клиент чужие заявки:
- `GET /events/my` — мои публикации (я капитан);
- `GET /applications/pending` — мои заявки, где жду решения капитана;
- `GET /applications/upcoming` — принятые заявки, то есть игры, в которых я участвую.

**Отмена / исключение** идут через одну функцию `event_service.cancel_acceptance`, которая возвращает место в `slots_available` и переводит событие из `full` обратно в `open`, если оно было заполнено. Обе стороны (капитан и игрок) получают уведомление в боте.

**Жизненный цикл событий**: API закрывает прошедшие события со временем `scheduled_at` в статус `completed`, чтобы они не висели в ленте и в разделе будущих игр. Прототип напоминаний (`reminder_service.py`) оставлен в коде, но не запускается из `main.py`; для продакшена напоминания лучше выносить в отдельный scheduler/worker.

## Про деньги — то, что осознанно не реализовано

В ТЗ два варианта: сбор капитаном напрямую (риск для платформы нулевой, но и контроля нет) или сбор на счёт платформы с последующим вручную ручным переводом владельцу площадки. Второй вариант требует реальной интеграции с платёжным провайдером (Kaspi, Stripe, ЮKassa — зависит от того, где вы физически принимаете деньги в Казахстане) и отдельной модели `Payment` со статусами `held / transferred / refunded`. Я не стал придумывать фейковую платёжную логику без реального провайдера — в модель `Event` уже заложено поле `price`, и расчёт «собрано» в `MyPublicationsTab.vue` сделан как `(slots_total - slots_available) * price`, то есть фактически взыскание привязано к подтверждённым местам, а не к самим заявкам. Когда выберете провайдера, на это место добавляется таблица `payments` и вебхук от платёжной системы — структура БД это не сломает.

## Запуск (дев-окружение)

```bash
cd backend
cp .env.example .env  # заполнить BOT_TOKEN, DATABASE_URL (строка от Supabase), WEBHOOK_BASE_URL
pip install -r requirements.txt
# создать таблицы: либо выполнить sql/schema.sql в Supabase SQL Editor,
# либо python -c "import asyncio; from app.database import engine, Base; from app import models; asyncio.run(...)"
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

Для вебхука бота нужен публичный HTTPS-адрес (например, через ngrok на этапе разработки) — он указывается в `WEBHOOK_BASE_URL`.
