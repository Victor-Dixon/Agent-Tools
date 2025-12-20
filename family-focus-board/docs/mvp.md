# MVP Plan — Family Focus Board

## Product

- **Name**: Family Focus Board
- **Tagline**: One board. One timer. One team.
- **Goal**: Build a shared Pomodoro + Kanban system for the family business so work is visible, time is protected, and follow-through becomes automatic.

## MVP definition (must-have)

- Org + team accounts (one shared workspace)
- Kanban board (Lists/Columns + Cards)
- Card fields: title, description, owner(s), due date, tags, checklist, links
- Pomodoro timer (25/5 default, configurable)
- Link Pomodoro sessions to a specific card
- Group “Focus Room”: when someone starts a session on a card, others can join
- Realtime updates (board changes + timer state)
- Activity log: who did what + when
- Basic stats: sessions per person, time per card, weekly totals

## Nice next

- Recurring tasks + templates
- Rewards ladder (points + streaks)
- Notifications + reminders
- Mobile PWA install
- Integrations (Discord webhooks, Google Calendar, Stripe later)

## UX rules

### Board

- Everything is a card
- A Pomodoro always belongs to a card
- Done means moved to Done + checklist complete

### Timer

- Focus 25m, Break 5m, Long break 15m after 4 sessions (configurable)
- Session creates a log record even if interrupted (with reason)
- Group room has a single source-of-truth timer state

## Milestones

- **M0: Repo + Infra**: monorepo scaffold, Postgres + migrations + seed, auth working
- **M1: Kanban Core**: CRUD + drag/drop, realtime board sync
- **M2: Pomodoro Core**: timer (local), session logging, link session to card
- **M3: Focus Room**: shared timer state per room, presence
- **M4: Stats + Accountability**: weekly rollups, per-person totals, per-card totals

## Validation gates

- Schema drift guard: migrations required
- Unit tests: timer state machine + permissions
- Integration tests: card move creates activity log
- E2E: create card -> start pomodoro -> complete -> move to Done

