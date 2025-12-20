import type { FastifyPluginAsync } from "fastify";
import type { Pool } from "pg";
import { pool } from "../db/pool.js";

declare module "fastify" {
  interface FastifyInstance {
    pg: Pool;
  }
}

export const dbPlugin: FastifyPluginAsync = async (fastify) => {
  fastify.decorate("pg", pool);
  fastify.addHook("onClose", async () => {
    await pool.end();
  });
};

