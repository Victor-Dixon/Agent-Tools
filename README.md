# Family Focus Board

Shared Pomodoro + Kanban for a family business: one board, one timer, one team.

## Monorepo layout

- `apps/web`: Next.js UI (board + timer + stats)
- `apps/api`: Fastify API + Socket.IO realtime gateway
- `packages/shared`: shared types + timer state machine
- `docs`: product + MVP docs

## Local dev (API + DB)

1) Start Postgres:

```bash
docker compose up -d
```

2) Configure env:

```bash
cp .env.example .env
```

3) Install deps:

```bash
npm install
```

4) Migrate + seed:

```bash
npm run db:migrate -w apps/api
npm run db:seed -w apps/api
```

5) Run API:

```bash
npm run dev -w apps/api
```

API defaults to `http://localhost:3001`.

### Auth (dev bootstrap)

For now, org scoping is enforced via headers:

- `x-org-id`
- `x-user-id`

Seed prints example IDs you can use for local calls.

