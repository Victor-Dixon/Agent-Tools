export type ID = string;

export type TimerMode = "focus" | "break" | "long_break";
export type SessionOutcome = "complete" | "interrupted" | "abandoned";

export type BoardEventName =
  | "board:list_updated"
  | "board:card_created"
  | "board:card_moved";

export type TimerEventName =
  | "timer:room_state"
  | "timer:started"
  | "timer:paused"
  | "timer:resumed"
  | "timer:ended";

export type PresenceEventName = "presence:user_joined" | "presence:user_left";

