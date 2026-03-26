# Nurvo Project Specification

## 1. Project Overview
**Nurvo** is an AI-powered educational training web game platform. It simulates nurse-patient communication scenarios, utilizing AI visuals, AI voice, and LLMs to allow nurses to practice in randomized, AI-generated simulation scenarios.

## 2. Technology Stack

### Frontend
- **Framework**: [Vue.js 3](https://vuejs.org/) (Composition API)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Routing**: [Vue Router](https://router.vuejs.org/)
- **Testing**: [Vitest](https://vitest.dev/)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Runtime**: Python 3.x

### Infrastructure & Services
- **Database & Authentication**: [Supabase](https://supabase.com/)
- **Voice Synthesis (TTS)**: [Eleven Labs](https://elevenlabs.io/)
- **LLM / AI Model**: [OpenAI GPT-4o](https://platform.openai.com/) (accessed via OpenAI API)
- **Digirunner**: For API management, traffic regulation, and enhanced security.

## 3. Architecture

### Client-Server Model
- **Frontend (`nurvofronted/`)**: Handles user interactions, visualizes simulation scenarios, and manages application state. Communicates with the backend via RESTful APIs.
- **Backend (`nurvobackend/`)**: Serves as the orchestration layer for AI services. It processes requests, interacts with Supabase for data persistence, generates scenarios via OpenAI GPT-4o, and manages voice synthesis.

## 4. Key Features (Planned/Inferred)
1.  **User Authentication**: Secure login and signup powered by Supabase.
2.  **Voice Interaction**: Realistic voice synthesis using Eleven Labs to convert text to speech for patient dialogue.
3.  **Intelligent Processing**: Using OpenAI GPT-4o to process user inputs and generate dynamic scenarios.
4.  **Responsive UI**: A modern, responsive interface built with Vue 3 and CSS.


## 5. Development Workflow
1.  **Frontend**:
    - Install dependencies: `npm install` (inside `nurvofronted/`)
    - Run dev server: `npm run dev`
2.  **Backend**:
    - Activate virtual environment: `source venv/bin/activate`
    - Install dependencies: `pip install -r requirements.txt`
    - Run FastAPI server (command to be defined via `uvicorn` or similar).

## 6. External Resources
- **UI Design**: [Canva Link](https://www.canva.com/design/DAHEF8M_KoU/_A96ERatW-9VF8yBo8md1Q/edit?utm_content=DAHEF8M_KoU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)
