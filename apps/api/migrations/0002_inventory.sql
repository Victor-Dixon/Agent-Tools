
create table if not exists inventory_categories (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  unique (org_id, name)
);

create table if not exists inventory_items (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  category_id uuid null references inventory_categories(id) on delete set null,
  name text not null,
  description text not null default '',
  value int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists inventory_items_org_id_idx on inventory_items(org_id);
create index if not exists inventory_items_category_id_idx on inventory_items(category_id);
create index if not exists inventory_items_value_idx on inventory_items(value desc);
