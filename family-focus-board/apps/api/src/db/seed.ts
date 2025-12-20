import { pool } from "./pool.js";

async function main(): Promise<void> {
  const orgRes = await pool.query<{ id: string }>(
    "insert into orgs (name) values ($1) returning id",
    ["Family Focus (Seed)"]
  );
  const orgId = orgRes.rows[0]!.id;

  const users = [
    { name: "Alex", email: "alex@example.com", role: "owner" },
    { name: "Sam", email: "sam@example.com", role: "member" }
  ];

  const userIds: string[] = [];
  for (const u of users) {
    const res = await pool.query<{ id: string }>(
      "insert into users (org_id, name, email, role) values ($1, $2, $3, $4) returning id",
      [orgId, u.name, u.email, u.role]
    );
    userIds.push(res.rows[0]!.id);
  }

  const boardRes = await pool.query<{ id: string }>(
    "insert into boards (org_id, name) values ($1, $2) returning id",
    [orgId, "Operations"]
  );
  const boardId = boardRes.rows[0]!.id;

  const listNames = [
    { name: "To do", sort: 0 },
    { name: "Doing", sort: 1 },
    { name: "Done", sort: 2 }
  ];

  const listIds: string[] = [];
  for (const l of listNames) {
    const res = await pool.query<{ id: string }>(
      "insert into lists (board_id, name, sort_order) values ($1, $2, $3) returning id",
      [boardId, l.name, l.sort]
    );
    listIds.push(res.rows[0]!.id);
  }

  await pool.query(
    "insert into focus_rooms (org_id, board_id, state_json) values ($1, $2, $3) on conflict (org_id, board_id) do nothing",
    [orgId, boardId, JSON.stringify({ phase: "idle" })]
  );

  // eslint-disable-next-line no-console
  console.log("Seed complete:");
  // eslint-disable-next-line no-console
  console.log({ orgId, boardId, listIds, userIds });
  // eslint-disable-next-line no-console
  console.log("Use headers for dev auth:", {
    "x-org-id": orgId,
    "x-user-id": userIds[0]
  });

  await pool.end();
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exitCode = 1;
});

