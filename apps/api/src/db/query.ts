import type { PoolClient, QueryResultRow } from "pg";
import { pool } from "./pool.js";

export async function withClient<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    return await fn(client);
  } finally {
    client.release();
  }
}

export async function tx<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
  return withClient(async (client) => {
    await client.query("begin");
    try {
      const res = await fn(client);
      await client.query("commit");
      return res;
    } catch (err) {
      await client.query("rollback");
      throw err;
    }
  });
}

export async function queryOne<T extends QueryResultRow>(
  sql: string,
  params: unknown[],
  client?: PoolClient
): Promise<T> {
  const runner = client ?? pool;
  const res = await runner.query<T>(sql, params);
  if (!res.rows[0]) throw new Error("Not found");
  return res.rows[0];
}

