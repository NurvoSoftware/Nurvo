## Context

`ChatPanel.vue` currently offers two targeting UIs that don't share state:
- **Tab buttons** (`:284-302`) call `switchTarget()` → `chatStore.setTarget()` → a single `currentTarget` (`'patient' | family_N`). `placeholder` and the empty-state text read `currentTarget`.
- **Plain-text `@mention`** (`:57-188`, commit `2dd8601`): typing `@` opens a dropdown (`allCharacters` / `filteredCharacters`); selecting inserts the literal `@名字 ` into the textarea. `handleSend()` re-parses the text (`/@(\S+)/g`, plus `@all`) into a `targets[]`, falling back to `[currentTarget]` when no `@` is present, then sends one `nurse_message` per target via `wsService.sendMessage(target, content)` — **including the `@名字` text in the content**.

The backend contract is per-message: `{ type: 'nurse_message', target, content }` (`wsService.ts:194-195`). It never reads mention text. So this change is purely a frontend UX rework.

## Goals / Non-Goals

**Goals:**
- One visible, removable chip per selected target; "who" is always visible.
- Message content is clean (no `@名字`).
- A single source of truth for targets, fed by both the `@` dropdown and the tab buttons.
- No regression to Chinese IME composing or the existing send/Enter behaviour.

**Non-Goals:**
- Inline-in-sentence chips (Slack-style chips *inside* the text flow).
- Backend / WebSocket contract changes.
- Reworking the dropdown's filtering logic (reused as-is).

## Decisions

### D1 — Chips live in a target bar above the textarea; the textarea stays a plain `<textarea>`
Render `selectedTargets` as a row of chips inside `.input-area`, directly above the existing `<textarea>`. The textarea keeps holding only the message text.
- **Why:** a native `<textarea>` cannot contain rich/interactive nodes, and this app is Traditional-Chinese-first — heavily IME-dependent. The team already added `event.isComposing` guards for the textarea. Keeping the textarea plain preserves that hard-won IME correctness and keeps the message trivially serialisable.
- **Alternative considered — `contenteditable` with inline chips (true Slack style):** rejected. `contenteditable` + Chinese IME is a well-known source of caret/composition/paste bugs; it would also complicate plain-text serialisation for `sendMessage` and accessibility. The cost far outweighs "chips sit inside the sentence." (If the user specifically wants inline chips later, that's a separate, larger change.)
- **Consequence:** the chip bar reads like an email "To:" field — arguably clearer for "who am I addressing" than inline tokens.

### D2 — `selectedTargetIds` is the single source of truth; it lives in `chatStore`
Replace `chatStore.currentTarget` (single) with `chatStore.selectedTargetIds: Ref<TargetId[]>`, where `TargetId = 'patient' | FamilySender | 'all'`. **It must live in the store, not the component**, because there are three sibling inputs under `SceneView`: the chat tab buttons, the `@` dropdown (both in `ChatPanel`), AND clicking a character in the 2D scene (`SceneFallback2D` → `SceneView.handleSelectTarget`). Store actions: `addTarget(id)` (de-dup; choosing `all` collapses to `['all']`; choosing an individual drops `all`), `toggleTarget(id)` (add/remove), `removeTarget(id)`, `clearTargets()`. The store holds only ids; the component derives chip display (name/gender) from `scenarioStore` so scenario data isn't duplicated.
- The `@` dropdown selection **adds**; tab buttons and scene-character clicks **toggle**; `tab-btn--active` reflects `selectedTargetIds.includes(id)`. `handleSend()` reads from `selectedTargetIds`.
- **Why:** eliminates the current split (`currentTarget` vs parsed text) and the ambiguity of which wins.
- **Alternative considered:** keep `currentTarget` for single-select and add a separate multi-select for `@` — rejected: two sources of truth is exactly the current problem.
- **`chatStore` change:** `placeholder` and empty-state currently read `chatStore.currentTarget`. Replace those reads with `selectedTargets` (e.g. placeholder = "輸入訊息給 王太太、王先生…"). `currentTarget`/`setTarget` become unused → remove them and the `typingIndicator` logic stays untouched (it's driven by the backend, not the target).

### D3 — `@all` is a distinct broadcast chip
Selecting "全部" sets `selectedTargets` to a single sentinel `{ id: 'all', … }` chip (clearing individual chips). `handleSend()` expands `all` to patient + every family id.
- **Why:** matches the existing `@all` broadcast intent while keeping the chip bar uncluttered.

### D4 — Empty selection defaults to patient
If `selectedTargets` is empty at send time, send to `['patient']`.
- **Why:** the patient is the primary interlocutor; never block the nurse. A placeholder hint ("預設對病患說話") communicates it.
- **Alternative considered:** disable send until a target is chosen — rejected as unnecessary friction for a timed exercise.

### D5 — Reuse the existing dropdown, change only the selection side-effect
`handleInput()` / `filteredCharacters` / the dropdown markup stay. Only `selectMention()` changes: instead of inserting `@名字 ` into the text, it pushes a chip and strips the in-progress `@query` from the textarea.

## Risks / Trade-offs

- **IME regression from touching the textarea handlers** → Mitigation: keep `@keydown.enter.exact="handleEnterKey"` and the `isComposing` guard exactly as-is; chips are added outside the compose path.
- **Stripping the `@query` mis-cuts multi-line / multiple `@`** → Mitigation: only strip from the last `@` to the caret (same span `handleInput` already tracks); cover with a unit test.
- **Removing `currentTarget` breaks a hidden consumer** → Mitigation: grep usages first (known: `ChatPanel` placeholder + empty state, `chatStore`); the `chatStore.spec`/`ChatPanel.spec` will catch breakage.
- **Chip bar grows tall with many targets** → Acceptable (max 4 characters); chips wrap.

## Migration Plan

Frontend-only, additive within one component. No data migration, no backend deploy. Rollback = revert the `ChatPanel.vue` / `chatStore.ts` / test changes. Validate by `npm run test:unit`, `npm run type-check`, and a manual smoke: type `@`, pick two characters → two chips → send → message bubble has no `@`, both NPCs reply.

## Resolved Decisions (confirmed with user)

- **Tab buttons toggle** (add when absent, remove when present), with the `tab-btn--active` highlight tracking whether the chip is selected. (D2)
- **The tab-button row stays** — buttons and the `@` dropdown both feed the one `selectedTargetIds` chip state; no UI is removed.

## Revealed during apply (artifact corrections)

- **State lives in `chatStore`, not the component** — a third targeting input exists: clicking a character in the 2D scene (`SceneFallback2D` emits `select-target` → `SceneView.handleSelectTarget` → was `setTarget`). It is a sibling of `ChatPanel`, so the shared selection must be in the store. `SceneView.handleSelectTarget` now calls `chatStore.toggleTarget`. (Corrects D2's "in the component".)
- **Chips persist after send** (not cleared per message) — matches the old `currentTarget`/button behaviour the user is replacing; clearing every send would force re-tagging each message.
- **`SceneFallback2D`'s `target` prop is pre-existing dead code** — `SceneView` never binds `:target`, so the scene doesn't highlight the active target today. Left as-is (out of scope); noted only.
- **`SceneCanvas3D` is commented out** in `SceneView` — ignored.
