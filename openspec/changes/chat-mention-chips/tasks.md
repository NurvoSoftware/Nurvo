## 1. Groundwork

- [x] 1.1 Grep all usages of `chatStore.currentTarget` / `setTarget` across the frontend. Found THREE consumers, not two: `ChatPanel.vue` (placeholder, empty state, send fallback, tab buttons), `chatStore.ts`, AND `SceneView.vue:57` (`handleSelectTarget` ← scene-character click via `SceneFallback2D` `select-target`). `SceneFallback2D`'s `target` prop is declared but never bound (dead). `SceneCanvas3D` is commented out. → state must live in the store.
- [x] 1.2 In `chatStore.ts`, add `selectedTargetIds: Ref<TargetId[]>` (`TargetId = 'patient' | FamilySender | 'all'`) + `addTarget`/`toggleTarget`/`removeTarget`/`clearTargets`; wire `reset()`. The component derives chip display (name/gender) from `scenarioStore`.

## 2. Chip model + send logic (TDD)

- [x] 2.1 RED: in `ChatPanel.spec.ts`, add a test — selecting two characters via the dropdown yields two chips and `sendMessage` is called once per target id with content that contains no `@`. Run → fails.
- [x] 2.2 GREEN: rework `selectMention()` to push a de-duped chip and strip the in-progress `@query` (last `@`→caret) from the textarea instead of inserting `@名字`.
- [x] 2.3 GREEN: rework `handleSend()` to read targets from `selectedTargetIds` (expand `all` → patient + families; empty → `['patient']`) and send the clean textarea content per target. Chips **persist** after send (do not clear) — matches the old button behaviour.
- [x] 2.4 RED→GREEN: add tests for the `全部` broadcast chip and for the empty-selection → patient default.

## 3. Chip bar + button unification (TDD)

- [x] 3.1 RED: add a test — clicking the 病患 tab button adds a 病患 chip; clicking the × on a chip removes it. Run → fails.
- [x] 3.2 GREEN: render the chip bar (avatar + name + × remove) above the textarea; add `addTarget()` / `removeTarget()` / `toggleTarget()` and point tab buttons at `toggleTarget()`; keep `tab-btn--active` highlight tracking whether that character's chip is selected.
- [x] 3.3 GREEN: update `placeholder` and the empty-state text to read `selectedTargets` instead of `currentTarget`.

## 4. Wire the scene + cleanup

- [x] 4.1 Point `SceneView.handleSelectTarget` at `chatStore.toggleTarget` (was `setTarget`) so scene-character clicks toggle the same chip state. (Leave `SceneFallback2D`'s unbound `target` prop alone — pre-existing dead code.)
- [x] 4.2 Remove the now-unused `currentTarget` / `setTarget` from `chatStore.ts` (defn, `reset()`, return) once nothing references them; update `chatStore`/`ChatPanel` tests that asserted `currentTarget`.
- [x] 4.3 Remove dead code left by the plain-text path (old `@名字` insertion branch, `switchTarget`).

## 5. Verify

- [x] 5.1 `npm run test:unit` (ChatPanel + chatStore green) + `npm run type-check` + `npm run lint`.
- [x] 5.2 Manual smoke DONE (2026-06-21, after `local-dev-env-setup` unblocked the auth/DB wall). Driven live against the running app (Vite → docker backend; real login + scenario + WebSocket): @ dropdown lists all targets; selecting one adds a chip and strips the `@query` from the textarea; a tab button toggles a chip on/off; chip `×` removes it without altering the text; sending with a chip puts CLEAN content (no `@`) in the bubble, the chip persists, and the targeted NPC (李美娟) replied over WS with TTS. IME guard verified: a synthetic `Enter` with `isComposing: true` does NOT send (real 注音 composition exercises the same guard; full IME composition can't be reproduced headlessly).

## 6. Close out

- [x] 6.1 Trace each spec requirement (chip add / remove / clean content / all-broadcast / empty-default) to its test; confirm covered.
- [x] 6.2 Ran `openspec validate chat-mention-chips` (valid); committed with user go-ahead.
