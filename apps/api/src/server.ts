import Fastify from "fastify";
import cors from "@fastify/cors";
import { env } from "./env.js";
import { dbPlugin } from "./plugins/db.js";
import { authPlugin } from "./plugins/auth.js";
import { routes } from "./routes.js";
import { initRealtime } from "./realtime.js";

async function buildServer() {
  const fastify = Fastify({
    logger: true
  });

  fastify.setErrorHandler((err: unknown, _req, reply) => {
    const e = err as any;
    // Validation
    if (e?.name === "ZodError") {
      return reply.code(400).send({ error: "validation_error", details: e.issues });
    }
    if (e?.message === "Not found") return reply.code(404).send({ error: "not_found" });
    if (e?.message === "Invalid list") return reply.code(400).send({ error: "invalid_list" });
    return reply.code(500).send({ error: "internal_error" });
  });

  await fastify.register(cors, {
    origin: true,
    credentials: true
  });

  await fastify.register(dbPlugin);
  await fastify.register(authPlugin);
  await fastify.register(routes);

  await initRealtime(fastify);

  return fastify;
}

buildServer()
  .then(async (app) => {
    await app.listen({ host: env.api.host, port: env.api.port });
  })
  .catch((err) => {
    // eslint-disable-next-line no-console
    console.error(err);
    process.exitCode = 1;
  });

