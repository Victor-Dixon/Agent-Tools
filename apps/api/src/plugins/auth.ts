import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { pool } from "../db/pool.js";

declare module "fastify" {
  interface FastifyRequest {
    auth: {
      orgId: string;
      userId: string;
      role: string;
    };
  }
}

const headersSchema = z.object({
  "x-org-id": z.string().uuid(),
  "x-user-id": z.string().uuid()
});

export const authPlugin: FastifyPluginAsync = async (fastify) => {
  fastify.addHook("preHandler", async (req, reply) => {
    // Allow bootstrap endpoints without headers.
    if (req.url === "/health") return;
    if (req.method === "POST" && req.url === "/orgs") return;

    const parsed = headersSchema.safeParse(req.headers);
    if (!parsed.success) {
      return reply.code(401).send({ error: "missing_or_invalid_auth_headers" });
    }

    const orgId = parsed.data["x-org-id"];
    const userId = parsed.data["x-user-id"];

    const res = await pool.query<{ role: string }>(
      "select role from users where id = $1 and org_id = $2",
      [userId, orgId]
    );
    if (!res.rows[0]) {
      return reply.code(403).send({ error: "forbidden" });
    }

    req.auth = { orgId, userId, role: res.rows[0].role };
  });
};

