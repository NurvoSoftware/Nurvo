## Why

Today a nurse picks who they are talking to in two parallel, half-overlapping ways: a row of **tab-bar buttons** (`ChatPanel.vue:284-302`, sets a single `chatStore.currentTarget`) and a **plain-text `@mention`** added by teammate kcurtis0618 in `2dd8601` (`ChatPanel.vue:57-188`, parses `@名字` out of the message text at send time). The `@` path works but the target is invisible once typed — it's just literal text like `@王太太` that also leaks into the message the NPC receives, and there is no way to see or remove a chosen target except by editing the raw string. The user wants a clear **visual tag chip** mechanism: selecting a character shows a removable chip, so "who am I addressing" is always visible and the message body stays clean.

## What Changes

- **Add removable visual tag chips** for the conversation target(s). Selecting a character via the `@` dropdown (or a tab button) adds a chip to a target bar in the input area; each chip shows avatar + name and an × to remove it.
- **Strip the `@query` from the textarea on selection** — the chip becomes the source of truth for the target, so the message text no longer contains `@名字`. The NPC receives a clean message.
- **Make chips the single source of truth for targeting.** Both the `@` dropdown and the existing tab buttons feed one `selectedTargets` list (the chips), removing the current split between `currentTarget` and the parsed-text targets.
- **`@all` becomes an "全部" chip** that broadcasts to every character; selecting it replaces individual chips.
- **Define the empty-state fallback**: if no chip is selected, the message defaults to the patient (never blocks sending).
- **Add component tests** for chip add/remove/send behaviour, and update the existing `ChatPanel.spec.ts`.

This changes externally observable chat behaviour (message content no longer carries `@名字`; targeting UI changes) — **BREAKING** for anything that relied on the literal `@mention` text reaching the backend (nothing in this repo does; the backend only reads the per-message `target` field).

## Capabilities

### New Capabilities
- `chat-mention-chips`: The chat input SHALL let the nurse select one or more conversation targets as removable visual tag chips (via an `@` dropdown or tab buttons), keep the message body free of mention text, broadcast when "all" is chosen, and default to the patient when no chip is selected.

### Modified Capabilities
<!-- None — no existing spec files in openspec/specs/ describe the chat input. -->

## Impact

- **Code (frontend only):**
  - `nurvofronted/src/components/game/ChatPanel.vue` — replace plain-text `@` insertion with a `selectedTargets` chip model; render the chip bar; rework `handleSend()` to read targets from chips and send a clean message; unify tab buttons + `@` into the chip state; update `placeholder`/empty-state that read `currentTarget`.
  - `nurvofronted/src/stores/chatStore.ts` — possibly replace `currentTarget`/`setTarget` with a `selectedTargets` list (or keep `currentTarget` for back-compat and derive). Decided in `design.md`.
- **Tests:** `nurvofronted/src/__tests__/ChatPanel.spec.ts` (update) + new chip-behaviour cases.
- **No backend change:** the WebSocket `nurse_message{target}` contract (`wsService.ts:164-195`) is unchanged — chips still resolve to the same `'patient' | family_N` ids, sent one message per target.
- **Out of scope:** inline-in-sentence chips via `contenteditable` (rejected for Chinese-IME risk — see `design.md`); changing the backend target model; styling beyond the chip component.
