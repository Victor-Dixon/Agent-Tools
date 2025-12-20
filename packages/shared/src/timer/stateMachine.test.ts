import { describe, expect, it } from "vitest";
import { DEFAULT_TIMER_CONFIG, initialRoomTimerState, transitionRoomTimer } from "./stateMachine";

describe("timer state machine", () => {
  it("requires a card before starting", () => {
    const s0 = initialRoomTimerState();
    expect(() =>
      transitionRoomTimer(s0, { type: "TIMER/START", nowMs: 0, sessionId: "s1" })
    ).toThrow(/belong to a card/i);
  });

  it("starts, pauses, resumes, and completes on tick", () => {
    const now0 = 1_000;
    const s0 = transitionRoomTimer(initialRoomTimerState(), { type: "ROOM/ATTACH_CARD", cardId: "c1" }).state;
    const started = transitionRoomTimer(s0, { type: "TIMER/START", nowMs: now0, sessionId: "sess1", plannedSeconds: 10 });

    expect(started.state.phase).toBe("running");
    expect(started.effects[0]).toMatchObject({ type: "SESSION/STARTED", sessionId: "sess1" });

    const paused = transitionRoomTimer(started.state, { type: "TIMER/PAUSE", nowMs: now0 + 2_000 });
    expect(paused.state.phase).toBe("paused");

    const resumed = transitionRoomTimer(paused.state, { type: "TIMER/RESUME", nowMs: now0 + 5_000 });
    expect(resumed.state.phase).toBe("running");

    // tick beyond completion (10s planned, ~3s paused)
    const done = transitionRoomTimer(resumed.state, { type: "TIMER/TICK", nowMs: now0 + 20_000 });
    expect(done.state.phase).toBe("ended");
    expect(done.effects.some((e) => e.type === "SESSION/ENDED")).toBe(true);
    const ended = done.effects.find((e) => e.type === "SESSION/ENDED");
    expect(ended).toMatchObject({ outcome: "complete", sessionId: "sess1" });
  });

  it("advances from focus -> break, and long break after 4 focus sessions", () => {
    let s = initialRoomTimerState(DEFAULT_TIMER_CONFIG);
    s = transitionRoomTimer(s, { type: "ROOM/ATTACH_CARD", cardId: "c1" }).state;

    for (let i = 1; i <= 4; i += 1) {
      const started = transitionRoomTimer(s, { type: "TIMER/START", nowMs: i * 1_000, sessionId: `sess${i}`, mode: "focus", plannedSeconds: 1 });
      const ended = transitionRoomTimer(started.state, { type: "TIMER/TICK", nowMs: i * 1_000 + 5_000 });
      s = ended.state;
      if (i < 4) expect(s.mode).toBe("break");
      if (i === 4) expect(s.mode).toBe("long_break");
      // simulate ending the break quickly to return to focus
      const breakStarted = transitionRoomTimer(s, { type: "TIMER/START", nowMs: i * 1_000 + 6_000, sessionId: `break${i}`, plannedSeconds: 1 }).state;
      s = transitionRoomTimer(breakStarted, { type: "TIMER/TICK", nowMs: i * 1_000 + 10_000 }).state;
      expect(s.mode).toBe("focus");
    }
  });
});

