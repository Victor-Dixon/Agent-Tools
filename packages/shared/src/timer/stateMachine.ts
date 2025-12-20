import type { TimerMode } from "../types";

export type TimerPhase = "idle" | "running" | "paused" | "ended";

export type TimerConfig = {
  focusSeconds: number;
  breakSeconds: number;
  longBreakSeconds: number;
  longBreakEvery: number; // e.g. 4
};

export type RoomTimerState = {
  phase: TimerPhase;
  mode: TimerMode;
  activeCardId: string | null;
  activeSessionId: string | null;
  startedAtMs: number | null; // epoch ms
  plannedSeconds: number;
  pausedAtMs: number | null; // epoch ms
  pauseAccumulatedMs: number; // total paused duration
  endedAtMs: number | null;
  cycleCount: number; // completed focus sessions since last long break
};

export type TimerEvent =
  | { type: "ROOM/ATTACH_CARD"; cardId: string }
  | { type: "ROOM/CLEAR_CARD" }
  | { type: "TIMER/START"; nowMs: number; sessionId: string; mode?: TimerMode; plannedSeconds?: number }
  | { type: "TIMER/PAUSE"; nowMs: number }
  | { type: "TIMER/RESUME"; nowMs: number }
  | { type: "TIMER/END"; nowMs: number; outcome: "complete" | "interrupted" | "abandoned"; note?: string }
  | { type: "TIMER/TICK"; nowMs: number };

export type TimerTransitionResult = {
  state: RoomTimerState;
  derived: {
    remainingSeconds: number;
    endsAtMs: number | null;
    isOverdue: boolean;
  };
  effects: Array<
    | { type: "SESSION/STARTED"; sessionId: string; mode: TimerMode; plannedSeconds: number }
    | { type: "SESSION/ENDED"; sessionId: string; outcome: "complete" | "interrupted" | "abandoned"; actualSeconds: number; note?: string }
  >;
};

export const DEFAULT_TIMER_CONFIG: TimerConfig = {
  focusSeconds: 25 * 60,
  breakSeconds: 5 * 60,
  longBreakSeconds: 15 * 60,
  longBreakEvery: 4
};

export function initialRoomTimerState(config: TimerConfig = DEFAULT_TIMER_CONFIG): RoomTimerState {
  return {
    phase: "idle",
    mode: "focus",
    activeCardId: null,
    activeSessionId: null,
    startedAtMs: null,
    plannedSeconds: config.focusSeconds,
    pausedAtMs: null,
    pauseAccumulatedMs: 0,
    endedAtMs: null,
    cycleCount: 0
  };
}

export function computePlannedSeconds(config: TimerConfig, mode: TimerMode, cycleCount: number): number {
  if (mode === "focus") return config.focusSeconds;
  if (mode === "long_break") return config.longBreakSeconds;
  // break
  // If we're about to start a break after completing focus #N and N hits longBreakEvery, prefer long break.
  // This is only used when mode is explicitly "break"; caller can choose long_break instead.
  void cycleCount;
  return config.breakSeconds;
}

function derive(state: RoomTimerState, nowMs: number): TimerTransitionResult["derived"] {
  if (state.phase === "idle") return { remainingSeconds: state.plannedSeconds, endsAtMs: null, isOverdue: false };
  if (state.phase === "ended") return { remainingSeconds: 0, endsAtMs: state.endedAtMs, isOverdue: false };
  if (state.startedAtMs == null) return { remainingSeconds: state.plannedSeconds, endsAtMs: null, isOverdue: false };

  const baseEnd = state.startedAtMs + state.plannedSeconds * 1000 + state.pauseAccumulatedMs;
  const effectiveEnd = state.phase === "paused" && state.pausedAtMs != null ? baseEnd + (nowMs - state.pausedAtMs) : baseEnd;
  const remainingMs = effectiveEnd - nowMs;
  const remainingSeconds = Math.max(0, Math.ceil(remainingMs / 1000));
  return { remainingSeconds, endsAtMs: effectiveEnd, isOverdue: remainingMs < 0 };
}

function actualSecondsSoFar(state: RoomTimerState, nowMs: number): number {
  if (state.startedAtMs == null) return 0;
  const effectiveNowMs = state.phase === "paused" && state.pausedAtMs != null ? state.pausedAtMs : nowMs;
  const elapsedMs = Math.max(0, effectiveNowMs - state.startedAtMs - state.pauseAccumulatedMs);
  return Math.floor(elapsedMs / 1000);
}

export function transitionRoomTimer(
  prev: RoomTimerState,
  event: TimerEvent,
  config: TimerConfig = DEFAULT_TIMER_CONFIG
): TimerTransitionResult {
  let state: RoomTimerState = { ...prev };
  const effects: TimerTransitionResult["effects"] = [];

  switch (event.type) {
    case "ROOM/ATTACH_CARD": {
      state.activeCardId = event.cardId;
      break;
    }
    case "ROOM/CLEAR_CARD": {
      // Can't clear while running.
      if (state.phase === "running" || state.phase === "paused") break;
      state.activeCardId = null;
      break;
    }
    case "TIMER/START": {
      if (!state.activeCardId) throw new Error("A Pomodoro must belong to a card.");
      if (state.phase === "running" || state.phase === "paused") break;

      const nextMode: TimerMode = event.mode ?? state.mode ?? "focus";
      const plannedSeconds =
        event.plannedSeconds ?? computePlannedSeconds(config, nextMode, state.cycleCount);

      state = {
        ...state,
        phase: "running",
        mode: nextMode,
        activeSessionId: event.sessionId,
        startedAtMs: event.nowMs,
        plannedSeconds,
        pausedAtMs: null,
        pauseAccumulatedMs: 0,
        endedAtMs: null
      };

      effects.push({ type: "SESSION/STARTED", sessionId: event.sessionId, mode: nextMode, plannedSeconds });
      break;
    }
    case "TIMER/PAUSE": {
      if (state.phase !== "running") break;
      state.phase = "paused";
      state.pausedAtMs = event.nowMs;
      break;
    }
    case "TIMER/RESUME": {
      if (state.phase !== "paused" || state.pausedAtMs == null) break;
      state.phase = "running";
      state.pauseAccumulatedMs += Math.max(0, event.nowMs - state.pausedAtMs);
      state.pausedAtMs = null;
      break;
    }
    case "TIMER/TICK": {
      // If time is up while running, auto-complete.
      const d = derive(state, event.nowMs);
      if (state.phase === "running" && d.remainingSeconds === 0 && state.activeSessionId) {
        const actualSeconds = actualSecondsSoFar(state, event.nowMs);
        const endedSessionId = state.activeSessionId;

        state.phase = "ended";
        state.endedAtMs = event.nowMs;
        state.activeSessionId = null;
        state.startedAtMs = null;
        state.pausedAtMs = null;
        state.pauseAccumulatedMs = 0;

        // Update cycle + next mode.
        if (state.mode === "focus") {
          state.cycleCount += 1;
          const shouldLongBreak = state.cycleCount % config.longBreakEvery === 0;
          state.mode = shouldLongBreak ? "long_break" : "break";
          state.plannedSeconds = computePlannedSeconds(
            config,
            state.mode,
            state.cycleCount
          );
        } else {
          state.mode = "focus";
          state.plannedSeconds = computePlannedSeconds(config, "focus", state.cycleCount);
        }

        effects.push({
          type: "SESSION/ENDED",
          sessionId: endedSessionId,
          outcome: "complete",
          actualSeconds
        });
      }
      break;
    }
    case "TIMER/END": {
      if (state.phase !== "running" && state.phase !== "paused") break;
      if (!state.activeSessionId) break;

      const actualSeconds = actualSecondsSoFar(state, event.nowMs);
      const endedSessionId = state.activeSessionId;

      state.phase = "ended";
      state.endedAtMs = event.nowMs;
      state.activeSessionId = null;
      state.startedAtMs = null;
      state.pausedAtMs = null;
      state.pauseAccumulatedMs = 0;

      // If they completed a focus session via explicit end, also advance.
      if (event.outcome === "complete") {
        if (state.mode === "focus") {
          state.cycleCount += 1;
          const shouldLongBreak = state.cycleCount % config.longBreakEvery === 0;
          state.mode = shouldLongBreak ? "long_break" : "break";
          state.plannedSeconds = computePlannedSeconds(config, state.mode, state.cycleCount);
        } else {
          state.mode = "focus";
          state.plannedSeconds = computePlannedSeconds(config, "focus", state.cycleCount);
        }
      }

      effects.push({
        type: "SESSION/ENDED",
        sessionId: endedSessionId,
        outcome: event.outcome,
        actualSeconds,
        note: event.note
      });
      break;
    }
    default: {
      // Exhaustiveness.
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const _never: never = event;
      break;
    }
  }

  return { state, derived: derive(state, "nowMs" in event ? event.nowMs : Date.now()), effects };
}

