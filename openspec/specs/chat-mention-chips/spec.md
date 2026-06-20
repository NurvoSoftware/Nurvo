# chat-mention-chips Specification

## Purpose
TBD - created by archiving change chat-mention-chips. Update Purpose after archive.
## Requirements
### Requirement: Select a target as a visual chip

The chat input SHALL let the nurse add a conversation target as a removable visual tag chip. Typing `@` SHALL open the existing character dropdown (patient + family members); choosing an entry SHALL add a chip showing that character's avatar and name, and SHALL remove the typed `@` and its query text from the message textarea.

#### Scenario: Selecting from the @ dropdown adds a chip
- **WHEN** the nurse types `@` and selects 王太太 from the dropdown
- **THEN** a chip labelled 王太太 appears in the target bar
- **AND** the textarea no longer contains the `@` or the query text

#### Scenario: A tab button adds the same chip
- **WHEN** the nurse clicks the 病患 tab button
- **THEN** a 病患 chip is present in the target bar (the same `selectedTargets` state the `@` dropdown feeds)

### Requirement: Remove a target chip

Each chip SHALL have a control to remove it, and removing a chip SHALL drop that character from the selected targets without altering the message text.

#### Scenario: Removing a chip
- **WHEN** the nurse clicks the × on the 王太太 chip
- **THEN** the 王太太 chip disappears from the target bar
- **AND** the message text in the textarea is unchanged

### Requirement: Message body excludes mention text

When a message is sent, its content SHALL be the textarea text only, with no `@名字` mention tokens. The targets SHALL come from the selected chips, and one `nurse_message` SHALL be sent per selected target using its existing id (`patient` / `family_0..2`).

#### Scenario: Clean content sent to each target
- **WHEN** chips 病患 and 王太太 are selected and the nurse sends "請問哪裡痛？"
- **THEN** `sendMessage` is called once for `patient` and once for the family id of 王太太
- **AND** every sent content equals "請問哪裡痛？" with no `@` token

### Requirement: Broadcast with the "all" chip

Selecting "全部" (all) SHALL produce a single broadcast chip that targets every character; while it is present, sending SHALL deliver the message to the patient and all family members.

#### Scenario: All chip broadcasts
- **WHEN** the "全部" chip is selected and the nurse sends a message
- **THEN** `sendMessage` is called for the patient and for each family member exactly once

### Requirement: Default target when no chip is selected

If no chip is selected, sending a message SHALL default to the patient so the nurse is never blocked from sending.

#### Scenario: Empty selection defaults to patient
- **WHEN** no chip is selected and the nurse sends "您好"
- **THEN** `sendMessage` is called once with target `patient`

