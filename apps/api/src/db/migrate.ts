import { readdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { pool } from "./pool.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const migrationsDir = join(__dirname, "..", "..", "migrations");

async function ensureMigrationsTable(): Promise<void> {
  await pool.query(`
    create table if not exists schema_migrations (
      id text primary key,
      applied_at timestamptz not null default now()
    );
  `);
}

async function appliedMigrationIds(): Promise<Set<string>> {
  const res = await pool.query<{ id: string }>("select id from schema_migrations order by id asc");
  return new Set(res.rows.map((r) => r.id));
}

async function applyMigration(id: string, sql: string): Promise<void> {
  const client = await pool.connect();
  try {
    await client.query("begin");
    await client.query(sql);
    await client.query("insert into schema_migrations (id) values ($1)", [id]);
    await client.query("commit");
    // eslint-disable-next-line no-console
    console.log(`applied migration ${id}`);
  } catch (err) {
    await client.query("rollback");
    throw err;
  } finally {
    client.release();
  }
}

async function main(): Promise<void> {
  await ensureMigrationsTable();

  const files = (await readdir(migrationsDir))
    .filter((f) => f.endsWith(".sql"))
    .sort((a, b) => a.localeCompare(b));

  const applied = await appliedMigrationIds();

  for (const filename of files) {
    if (applied.has(filename)) continue;
    const sql = await readFile(join(migrationsDir, filename), "utf8");
    await applyMigration(filename, sql);
  }

  // eslint-disable-next-line no-console
  console.log("migrations up to date");
  await pool.end();
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exitCode = 1;
});

