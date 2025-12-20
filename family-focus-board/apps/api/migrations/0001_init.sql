-- Schema drift guard: all changes go through migrations.

create extension if not exists pgcrypto;

create table if not exists schema_migrations (
  id text primary key,
  applied_at timestamptz not null default now()
);

create table if not exists orgs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  email text not null,
  role text not null default 'member',
  created_at timestamptz not null default now(),
  unique (org_id, email)
);

create table if not exists boards (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists lists (
  id uuid primary key default gen_random_uuid(),
  board_id uuid not null references boards(id) on delete cascade,
  name text not null,
  sort_order int not null default 0
);

create table if not exists cards (
  id uuid primary key default gen_random_uuid(),
  board_id uuid not null references boards(id) on delete cascade,
  list_id uuid not null references lists(id) on delete restrict,
  title text not null,
  description text not null default '',
  due_at timestamptz null,
  status text not null default 'open',
  priority int not null default 0,
  links_json jsonb not null default '[]'::jsonb,
  created_by uuid null references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists cards_board_id_idx on cards(board_id);
create index if not exists cards_list_id_idx on cards(list_id);

create table if not exists card_assignees (
  card_id uuid not null references cards(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  primary key (card_id, user_id)
);

create table if not exists card_tags (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  unique (org_id, name)
);

create table if not exists card_tag_map (
  card_id uuid not null references cards(id) on delete cascade,
  tag_id uuid not null references card_tags(id) on delete cascade,
  primary key (card_id, tag_id)
);

create table if not exists checklists (
  id uuid primary key default gen_random_uuid(),
  card_id uuid not null references cards(id) on delete cascade,
  title text not null
);

create table if not exists checklist_items (
  id uuid primary key default gen_random_uuid(),
  checklist_id uuid not null references checklists(id) on delete cascade,
  text text not null,
  is_done boolean not null default false,
  sort_order int not null default 0
);

create table if not exists focus_rooms (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  board_id uuid not null references boards(id) on delete cascade,
  active_card_id uuid null references cards(id) on delete set null,
  state_json jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  unique (org_id, board_id)
);

create table if not exists pomodoro_sessions (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  board_id uuid not null references boards(id) on delete cascade,
  card_id uuid not null references cards(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  room_id uuid null references focus_rooms(id) on delete set null,
  mode text not null check (mode in ('focus', 'break', 'long_break')),
  planned_seconds int not null,
  actual_seconds int null,
  started_at timestamptz not null default now(),
  ended_at timestamptz null,
  outcome text null check (outcome in ('complete', 'interrupted', 'abandoned')),
  note text null
);

create index if not exists pomodoro_sessions_org_id_idx on pomodoro_sessions(org_id);
create index if not exists pomodoro_sessions_user_id_idx on pomodoro_sessions(user_id);
create index if not exists pomodoro_sessions_card_id_idx on pomodoro_sessions(card_id);

create table if not exists activity_log (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  actor_user_id uuid null references users(id) on delete set null,
  entity_type text not null,
  entity_id uuid null,
  action text not null,
  meta_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists activity_log_org_created_idx on activity_log(org_id, created_at desc);

