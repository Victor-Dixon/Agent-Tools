import type { PoolClient } from "pg";

export async function logActivity(
  client: PoolClient,
  input: {
    orgId: string;
    actorUserId: string | null;
    entityType: string;
    entityId: string | null;
    action: string;
    meta?: unknown;
  }
): Promise<void> {
  await client.query(
    `insert into activity_log (org_id, actor_user_id, entity_type, entity_id, action, meta_json)
     values ($1, $2, $3, $4, $5, $6)`,
    [
      input.orgId,
      input.actorUserId,
      input.entityType,
      input.entityId,
      input.action,
      JSON.stringify(input.meta ?? {})
    ]
  );
}

