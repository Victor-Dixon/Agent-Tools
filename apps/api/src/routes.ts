import type { FastifyPluginAsync } from "fastify";
import { z } from "zod";
import { tx } from "./db/query.js";
import { logActivity } from "./activity.js";
import { emitBoard } from "./realtime.js";
import { transitionRoomTimer, initialRoomTimerState, DEFAULT_TIMER_CONFIG } from "@ffb/shared";

const uuid = z.string().uuid();

export const routes: FastifyPluginAsync = async (fastify) => {
  fastify.get("/health", async () => ({ ok: true }));

  fastify.post("/orgs", async (req, reply) => {
    const body = z
      .object({
        orgName: z.string().min(1),
        ownerName: z.string().min(1),
        ownerEmail: z.string().email()
      })
      .parse(req.body);

    const result = await tx(async (client) => {
      const orgRes = await client.query<{ id: string }>(
        "insert into orgs (name) values ($1) returning id",
        [body.orgName]
      );
      const orgId = orgRes.rows[0]!.id;

      const userRes = await client.query<{ id: string }>(
        "insert into users (org_id, name, email, role) values ($1, $2, $3, $4) returning id",
        [orgId, body.ownerName, body.ownerEmail, "owner"]
      );
      const userId = userRes.rows[0]!.id;

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "org",
        entityId: orgId,
        action: "org:created",
        meta: { ownerUserId: userId }
      });

      return { orgId, userId };
    });

    return reply.code(201).send(result);
  });

  fastify.get("/boards", async (req) => {
    const { orgId } = req.auth;
    const res = await fastify.pg.query(
      "select id, name, created_at from boards where org_id = $1 order by created_at asc",
      [orgId]
    );
    return { boards: res.rows };
  });

  fastify.post("/boards", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const body = z.object({ name: z.string().min(1) }).parse(req.body);

    const out = await tx(async (client) => {
      const res = await client.query<{ id: string; name: string; created_at: string }>(
        "insert into boards (org_id, name) values ($1, $2) returning id, name, created_at",
        [orgId, body.name]
      );
      const board = res.rows[0]!;

      await client.query(
        "insert into focus_rooms (org_id, board_id, state_json) values ($1, $2, $3) on conflict (org_id, board_id) do nothing",
        [orgId, board.id, JSON.stringify(initialRoomTimerState(DEFAULT_TIMER_CONFIG))]
      );

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "board",
        entityId: board.id,
        action: "board:created",
        meta: { name: board.name }
      });

      return board;
    });

    return reply.code(201).send(out);
  });

  fastify.post("/boards/:id/lists", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const boardId = uuid.parse((req.params as any).id);
    const body = z.object({ name: z.string().min(1), sortOrder: z.number().int().optional() }).parse(req.body);

    const out = await tx(async (client) => {
      const board = await client.query<{ id: string }>("select id from boards where id = $1 and org_id = $2", [
        boardId,
        orgId
      ]);
      if (!board.rows[0]) throw new Error("Not found");

      const res = await client.query<{ id: string; name: string; sort_order: number }>(
        "insert into lists (board_id, name, sort_order) values ($1, $2, $3) returning id, name, sort_order",
        [boardId, body.name, body.sortOrder ?? 0]
      );
      const list = res.rows[0]!;

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "list",
        entityId: list.id,
        action: "list:created",
        meta: { boardId, name: list.name, sortOrder: list.sort_order }
      });

      emitBoard(fastify, boardId, "board:list_updated", { boardId });
      return list;
    });

    return reply.code(201).send(out);
  });

  fastify.post("/boards/:id/cards", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const boardId = uuid.parse((req.params as any).id);
    const body = z
      .object({
        listId: uuid,
        title: z.string().min(1),
        description: z.string().optional(),
        dueAt: z.string().datetime().optional(),
        priority: z.number().int().optional(),
        links: z.array(z.string().url()).optional(),
        assigneeIds: z.array(uuid).optional()
      })
      .parse(req.body);

    const out = await tx(async (client) => {
      const board = await client.query<{ id: string }>("select id from boards where id = $1 and org_id = $2", [
        boardId,
        orgId
      ]);
      if (!board.rows[0]) throw new Error("Not found");

      const list = await client.query<{ id: string }>(
        "select id from lists where id = $1 and board_id = $2",
        [body.listId, boardId]
      );
      if (!list.rows[0]) throw new Error("Invalid list");

      const res = await client.query<{ id: string }>(
        `insert into cards (board_id, list_id, title, description, due_at, priority, links_json, created_by)
         values ($1, $2, $3, $4, $5, $6, $7, $8)
         returning id`,
        [
          boardId,
          body.listId,
          body.title,
          body.description ?? "",
          body.dueAt ?? null,
          body.priority ?? 0,
          JSON.stringify(body.links ?? []),
          userId
        ]
      );
      const cardId = res.rows[0]!.id;

      for (const assigneeId of body.assigneeIds ?? []) {
        await client.query(
          "insert into card_assignees (card_id, user_id) values ($1, $2) on conflict do nothing",
          [cardId, assigneeId]
        );
      }

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "card",
        entityId: cardId,
        action: "card:created",
        meta: { boardId, listId: body.listId, title: body.title }
      });

      emitBoard(fastify, boardId, "board:card_created", { boardId, cardId, listId: body.listId });
      return { id: cardId };
    });

    return reply.code(201).send(out);
  });

  fastify.patch("/cards/:id", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const cardId = uuid.parse((req.params as any).id);
    const body = z
      .object({
        title: z.string().min(1).optional(),
        description: z.string().optional(),
        dueAt: z.string().datetime().nullable().optional(),
        priority: z.number().int().optional(),
        listId: uuid.optional(),
        status: z.string().optional()
      })
      .parse(req.body);

    const out = await tx(async (client) => {
      const existing = await client.query<{ board_id: string; list_id: string }>(
        `select c.board_id, c.list_id
         from cards c
         join boards b on b.id = c.board_id
         where c.id = $1 and b.org_id = $2`,
        [cardId, orgId]
      );
      const row = existing.rows[0];
      if (!row) throw new Error("Not found");

      const nextListId = body.listId ?? row.list_id;
      if (body.listId) {
        const listOk = await client.query<{ id: string }>("select id from lists where id = $1 and board_id = $2", [
          nextListId,
          row.board_id
        ]);
        if (!listOk.rows[0]) throw new Error("Invalid list");
      }

      const fields: string[] = [];
      const params: unknown[] = [];
      let idx = 1;

      function setField(col: string, value: unknown): void {
        fields.push(`${col} = $${idx}`);
        params.push(value);
        idx += 1;
      }

      if (body.title !== undefined) setField("title", body.title);
      if (body.description !== undefined) setField("description", body.description);
      if (body.dueAt !== undefined) setField("due_at", body.dueAt);
      if (body.priority !== undefined) setField("priority", body.priority);
      if (body.status !== undefined) setField("status", body.status);
      if (body.listId !== undefined) setField("list_id", body.listId);
      setField("updated_at", new Date().toISOString());

      params.push(cardId);
      const sql = `update cards set ${fields.join(", ")} where id = $${idx} returning id, board_id, list_id`;
      const updated = await client.query<{ id: string; board_id: string; list_id: string }>(sql, params);

      if (body.listId && body.listId !== row.list_id) {
        await logActivity(client, {
          orgId,
          actorUserId: userId,
          entityType: "card",
          entityId: cardId,
          action: "card:moved",
          meta: { fromListId: row.list_id, toListId: body.listId, boardId: row.board_id }
        });
        emitBoard(fastify, row.board_id, "board:card_moved", {
          boardId: row.board_id,
          cardId,
          fromListId: row.list_id,
          toListId: body.listId
        });
      } else {
        await logActivity(client, {
          orgId,
          actorUserId: userId,
          entityType: "card",
          entityId: cardId,
          action: "card:updated",
          meta: Object.keys(body)
        });
      }

      return updated.rows[0]!;
    });

    return reply.send(out);
  });

  fastify.post("/cards/:id/checklists", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const cardId = uuid.parse((req.params as any).id);
    const body = z.object({ title: z.string().min(1) }).parse(req.body);

    const out = await tx(async (client) => {
      const card = await client.query<{ board_id: string }>(
        `select c.board_id
         from cards c join boards b on b.id = c.board_id
         where c.id = $1 and b.org_id = $2`,
        [cardId, orgId]
      );
      if (!card.rows[0]) throw new Error("Not found");

      const res = await client.query<{ id: string }>(
        "insert into checklists (card_id, title) values ($1, $2) returning id",
        [cardId, body.title]
      );

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "checklist",
        entityId: res.rows[0]!.id,
        action: "checklist:created",
        meta: { cardId, title: body.title }
      });

      emitBoard(fastify, card.rows[0]!.board_id, "board:list_updated", { cardId });
      return { id: res.rows[0]!.id };
    });

    return reply.code(201).send(out);
  });

  fastify.post("/cards/:id/sessions/start", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const cardId = uuid.parse((req.params as any).id);
    const body = z
      .object({
        mode: z.enum(["focus", "break", "long_break"]).default("focus"),
        plannedSeconds: z.number().int().positive().optional()
      })
      .parse(req.body ?? {});

    const out = await tx(async (client) => {
      const card = await client.query<{ board_id: string }>(
        `select c.board_id
         from cards c join boards b on b.id = c.board_id
         where c.id = $1 and b.org_id = $2`,
        [cardId, orgId]
      );
      const cardRow = card.rows[0];
      if (!cardRow) throw new Error("Not found");

      const boardId = cardRow.board_id;

      const roomRes = await client.query<{ id: string; state_json: any }>(
        `insert into focus_rooms (org_id, board_id, active_card_id, state_json)
         values ($1, $2, $3, $4)
         on conflict (org_id, board_id)
         do update set active_card_id = excluded.active_card_id
         returning id, state_json`,
        [orgId, boardId, cardId, JSON.stringify(initialRoomTimerState(DEFAULT_TIMER_CONFIG))]
      );

      const roomId = roomRes.rows[0]!.id;
      const prevState = roomRes.rows[0]!.state_json ?? initialRoomTimerState(DEFAULT_TIMER_CONFIG);

      const sessionRes = await client.query<{ id: string; started_at: string }>(
        `insert into pomodoro_sessions (org_id, board_id, card_id, user_id, room_id, mode, planned_seconds)
         values ($1, $2, $3, $4, $5, $6, $7)
         returning id, started_at`,
        [orgId, boardId, cardId, userId, roomId, body.mode, body.plannedSeconds ?? DEFAULT_TIMER_CONFIG.focusSeconds]
      );
      const sessionId = sessionRes.rows[0]!.id;

      const nowMs = Date.now();
      const attached = transitionRoomTimer(prevState, { type: "ROOM/ATTACH_CARD", cardId });
      const next = transitionRoomTimer(attached.state, {
        type: "TIMER/START",
        nowMs,
        sessionId,
        mode: body.mode,
        plannedSeconds: body.plannedSeconds
      });

      await client.query(
        "update focus_rooms set state_json = $1, active_card_id = $2, updated_at = now() where id = $3",
        [JSON.stringify(next.state), cardId, roomId]
      );

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "pomodoro_session",
        entityId: sessionId,
        action: "timer:started",
        meta: { boardId, cardId, roomId, mode: body.mode, plannedSeconds: next.state.plannedSeconds }
      });

      emitBoard(fastify, boardId, "timer:started", { boardId, cardId, roomId, sessionId, state: next.state });
      emitBoard(fastify, boardId, "timer:room_state", { boardId, cardId, roomId, state: next.state });

      return { sessionId, roomId, boardId, state: next.state };
    });

    return reply.code(201).send(out);
  });

  fastify.post("/sessions/:id/stop", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const sessionId = uuid.parse((req.params as any).id);
    const body = z
      .object({
        outcome: z.enum(["complete", "interrupted", "abandoned"]).default("complete"),
        note: z.string().optional()
      })
      .parse(req.body ?? {});

    const out = await tx(async (client) => {
      const sess = await client.query<{
        id: string;
        board_id: string;
        card_id: string;
        room_id: string | null;
        started_at: string;
        planned_seconds: number;
      }>(
        `select s.id, s.board_id, s.card_id, s.room_id, s.started_at, s.planned_seconds
         from pomodoro_sessions s
         where s.id = $1 and s.org_id = $2`,
        [sessionId, orgId]
      );
      const row = sess.rows[0];
      if (!row) throw new Error("Not found");

      const now = new Date();
      const actualSeconds = Math.max(
        0,
        Math.floor((now.getTime() - new Date(row.started_at).getTime()) / 1000)
      );

      await client.query(
        `update pomodoro_sessions
         set ended_at = $1, actual_seconds = $2, outcome = $3, note = $4
         where id = $5`,
        [now.toISOString(), actualSeconds, body.outcome, body.note ?? null, sessionId]
      );

      if (row.room_id) {
        const room = await client.query<{ id: string; state_json: any }>(
          "select id, state_json from focus_rooms where id = $1 and org_id = $2",
          [row.room_id, orgId]
        );
        if (room.rows[0]) {
          const prevState = room.rows[0]!.state_json ?? initialRoomTimerState(DEFAULT_TIMER_CONFIG);
          const next = transitionRoomTimer(prevState, {
            type: "TIMER/END",
            nowMs: Date.now(),
            outcome: body.outcome,
            note: body.note
          });
          await client.query("update focus_rooms set state_json = $1, updated_at = now() where id = $2", [
            JSON.stringify(next.state),
            row.room_id
          ]);
          emitBoard(fastify, row.board_id, "timer:ended", {
            boardId: row.board_id,
            roomId: row.room_id,
            sessionId,
            outcome: body.outcome,
            actualSeconds
          });
          emitBoard(fastify, row.board_id, "timer:room_state", { boardId: row.board_id, state: next.state });
        }
      }

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "pomodoro_session",
        entityId: sessionId,
        action: "timer:ended",
        meta: { outcome: body.outcome, actualSeconds }
      });

      return { sessionId, outcome: body.outcome, actualSeconds };
    });

    return reply.send(out);
  });

  fastify.get("/stats/weekly", async (req) => {
    const { orgId } = req.auth;
    // ISO week range: [now-7d, now]
    const res = await fastify.pg.query(
      `select
         coalesce(sum(actual_seconds), 0) as total_seconds,
         count(*)::int as total_sessions
       from pomodoro_sessions
       where org_id = $1 and started_at >= (now() - interval '7 days')`,
      [orgId]
    );
    return { weekly: res.rows[0] ?? { total_seconds: 0, total_sessions: 0 } };
  });

  fastify.post("/inventory/categories", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const body = z.object({ name: z.string().min(1) }).parse(req.body);

    const out = await tx(async (client) => {
      const res = await client.query<{ id: string; name: string }>(
        "insert into inventory_categories (org_id, name) values ($1, $2) returning id, name",
        [orgId, body.name]
      );
      const category = res.rows[0]!;

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "inventory_category",
        entityId: category.id,
        action: "inventory_category:created",
        meta: { name: category.name }
      });

      return category;
    });

    return reply.code(201).send(out);
  });

  fastify.post("/inventory/items", async (req, reply) => {
    const { orgId, userId } = req.auth;
    const body = z
      .object({
        name: z.string().min(1),
        description: z.string().optional(),
        value: z.number().int().default(0),
        categoryId: uuid.optional()
      })
      .parse(req.body);

    const out = await tx(async (client) => {
      if (body.categoryId) {
        const cat = await client.query("select id from inventory_categories where id = $1 and org_id = $2", [
          body.categoryId,
          orgId
        ]);
        if (!cat.rows[0]) throw new Error("Invalid category");
      }

      const res = await client.query<{ id: string }>(
        "insert into inventory_items (org_id, category_id, name, description, value) values ($1, $2, $3, $4, $5) returning id",
        [orgId, body.categoryId, body.name, body.description ?? "", body.value]
      );
      const item = res.rows[0]!;

      await logActivity(client, {
        orgId,
        actorUserId: userId,
        entityType: "inventory_item",
        entityId: item.id,
        action: "inventory_item:created",
        meta: { name: body.name, value: body.value, categoryId: body.categoryId }
      });

      return item;
    });

    return reply.code(201).send(out);
  });

  fastify.get("/inventory/items", async (req) => {
    const { orgId } = req.auth;
    const query = z.object({ categoryId: uuid.optional() }).parse(req.query);

    let sql = `
        select i.*, c.name as category_name
        from inventory_items i
        left join inventory_categories c on c.id = i.category_id
        where i.org_id = $1
    `;
    const params: any[] = [orgId];

    if (query.categoryId) {
      sql += " and i.category_id = $2";
      params.push(query.categoryId);
    }

    sql += " order by i.value desc";

    const res = await fastify.pg.query(sql, params);
    return { items: res.rows };
  });
};

