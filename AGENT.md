# AI Agent Guidelines (AGENT.md)

This document provides instructions and context for AI agents (like GitHub Copilot, Cursor, etc.) working on the **Nurvo** project.

## 1. Context & Role
You are acting as an expert Full Stack Developer specializing in **Vue 3**, **TypeScript**, **Python (FastAPI)**, and **AI Integrations**. Your goal is to maintain high code quality, ensure type safety, and follow modern best practices for this **nurse-patient communication simulation game**.

**Important**: When executing tasks, always refer to `SPEC.md` for specific requirements, feature details, and architectural guidelines. Ensure your implementation aligns with the project specifications outlined there.

## 2. Project Structure & Scope
- **Root Directory**: Contains backend configuration, Python environment (`venv`), and general project docs.
- **`nurvofronted/`**: Contains the complete frontend application (Vue 3 + Vite).
- **`nurvobackend/`**: Contains the backend application (FastAPI).

**When working on files:**
- Always check which directory you are in.
- If editing frontend code, ensure you are working within `nurvofronted/`.
- If editing backend code, ensure you are working within `nurvobackend/`.

## 3. Technology Standards

### Frontend (Vue 3 + TS)
- **Composition API**: Always use `<script setup lang="ts">`.
- **Framework & Tooling**: Vue 3, Vite, Vue Router, Vitest.
- **Typing**: Use strict TypeScript types. Avoid `any` whenever possible.
- **State**: Use Pinia for global state management.
- **Styling**: Scoped CSS is preferred unless utilizing a global utility framework.
- **Components**: Follow the Single File Component (SFC) pattern.
- **File Naming**: PascalCase for components (e.g., `userProfile.vue` -> `UserProfile.vue`).

### Backend (Python + FastAPI)
- **Framework**: FastAPI (Python 3.x).
- **Type Hinting**: Use Python type hints heavily (Pydantic models are preferred).
- **Async**: Utilize `async/await` for I/O bound operations (DB calls, API requests).
- **Style**: Follow PEP 8 guidelines.
- **Dependencies**: Always ask to update `requirements.txt` if a new package is introduced.

## 4. External Integrations
- **Supabase**: Used for authentication and database. Frontend uses Supabase JS client; Backend uses Python client. Ensure keys are managed via environment variables.
- **AI Services**:
    - **Eleven Labs**: TTS for patient lines; **STT** for nurse speech input (same vendor or browser—see `docs/API.md`).
    - **Gemini (via Hugging Face or API)**: For LLM-based scenario generation and intelligent processing.
    - **OpenTPI / digiRunner**: API gateway & governance (see `docs/API.md`); public traffic goes through digiRunner, not raw FastAPI in production.
- **Handling AI APIs**: These are paid/limited APIs. Ensure robust error handling (e.g., graceful handling of rate limits or API failures).

## 5. Task Management
- If a task involves multiple steps (e.g., "Create a simulation scenario"), break it down:
    1.  Create frontend UI components for the scenario.
    2.  Implement backend logic to fetch AI-generated scripts (Gemini).
    3.  Integrate TTS (Eleven Labs) for voice output.
    4.  Ensure data persistence via Supabase.

## 6. Common Commands
- **Frontend Dev**: `cd nurvofronted && npm run dev`
- **Backend Setup**: `source venv/bin/activate` (then run server from `nurvobackend/`)

## 7. Safety & Security
- **NEVER** output real API keys or secrets in code blocks.
- **ALWAYS** suggest using `.env` files for sensitive data.
- **ALWAYS** check `.gitignore` before creating new large files or directories that shouldn't be committed.
