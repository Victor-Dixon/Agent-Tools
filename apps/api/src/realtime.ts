import type { FastifyInstance } from "fastify";
import { Server } from "socket.io";
import { pool } from "./db/pool.js";

declare module "fastify" {
  interface FastifyInstance {
    io: Server;
  }
}

function orgRoom(orgId: string): string {
  return `org:${orgId}`;
}

function boardRoom(boardId: string): string {
  return `board:${boardId}`;
}

export async function initRealtime(fastify: FastifyInstance): Promise<void> {
  const io = new Server(fastify.server, {
    cors: { origin: true, credentials: true }
  });

  fastify.decorate("io", io);

  io.on("connection", (socket) => {
    socket.on("join", async (payload: { orgId: string; boardId?: string; userId: string }) => {
      const { orgId, boardId, userId } = payload ?? {};
      if (!orgId || !userId) return;
      socket.data.orgId = orgId;
      socket.data.userId = userId;
      socket.join(orgRoom(orgId));

      if (boardId) {
        socket.data.boardId = boardId;
        socket.join(boardRoom(boardId));
        io.to(boardRoom(boardId)).emit("presence:user_joined", { userId });

        // Push current room timer state as single source of truth.
        const res = await pool.query<{ state_json: unknown; active_card_id: string | null }>(
          "select state_json, active_card_id from focus_rooms where org_id = $1 and board_id = $2",
          [orgId, boardId]
        );
        const row = res.rows[0];
        if (row) {
          socket.emit("timer:room_state", {
            boardId,
            activeCardId: row.active_card_id,
            state: row.state_json
          });
        }
      }
    });

    socket.on("leave", (payload: { boardId?: string }) => {
      const boardId: string | undefined = payload?.boardId ?? socket.data.boardId;
      const userId: string | undefined = socket.data.userId;
      if (boardId) socket.leave(boardRoom(boardId));
      if (boardId && userId) io.to(boardRoom(boardId)).emit("presence:user_left", { userId });
      socket.data.boardId = undefined;
    });

    socket.on("disconnect", () => {
      const boardId: string | undefined = socket.data.boardId;
      const userId: string | undefined = socket.data.userId;
      if (boardId && userId) io.to(boardRoom(boardId)).emit("presence:user_left", { userId });
    });
  });
}

export function emitOrg(fastify: FastifyInstance, orgId: string, event: string, payload: unknown): void {
  fastify.io.to(orgRoom(orgId)).emit(event, payload);
}

export function emitBoard(fastify: FastifyInstance, boardId: string, event: string, payload: unknown): void {
  fastify.io.to(boardRoom(boardId)).emit(event, payload);
}

