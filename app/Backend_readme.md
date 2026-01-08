# 🚀 Showcase AI - Backend Portfolio Engine

**Showcase AI** is an industry-grade backend infrastructure designed to transform raw resumes into stunning, professional portfolios using **Multi-Agent Systems** and **Google Gemini 1.5 Vision**.

[Image of a professional software architecture diagram showing the relationship between FastAPI, Firebase, PostgreSQL, and Google Gemini]

---

## 🏗️ Architecture Overview

The system is built on a **High-Performance Asynchronous Architecture** using industry-standard patterns:

* **FastAPI Framework**: Leveraging Python's `asyncio` for non-blocking I/O operations and high-concurrency handling.
* **Google Gemini 1.5 Vision**: Cloud-native OCR and document understanding, replacing traditional Tesseract with superior layout recognition and contextual awareness.
* **Firebase Authentication**: Enterprise-grade Google Sign-In integration with server-side JWT-based token verification.
* **SQLModel (PostgreSQL)**: A unified data layer combining the power of SQLAlchemy with Pydantic's type safety for resilient data persistence.
* **Background Task Orchestrator**: Offloading heavy AI generation and image processing to background worker threads to maintain sub-second API responsiveness.

---

## 🛡️ Security & Identity Management

We have implemented a **Zero-Trust Identity Flow** to ensure user data integrity:

1.  **Authentication**: Handled via Firebase Google Login on the client side.
2.  **Authorization**: The backend verifies every request using the **Firebase Admin SDK**, extracting the `uid` from the bearer token to ensure strict data ownership.
3.  **RBAC (Role-Based Access Control)**:
    * **Private**: Only the portfolio owner (matching Firebase `uid`) can edit or view drafts.
    * **Public**: Anyone can view a portfolio once it is marked `is_published` and assigned a custom URL slug.

[Image of a Firebase authentication flow diagram showing the frontend, Firebase server, and backend interaction]

---

## 🤖 AI Processing Pipeline

The backend serves as the orchestration layer for the **Agentic Intelligence**:

1.  **Ingestion**: Resumes (PDF/Images) are validated for size (5MB limit) and type before being streamed to the OCR Service.
2.  **Vision OCR**: Gemini 1.5 Flash extracts hierarchical Markdown text, preserving the visual structure of the original resume.
3.  **Agentic Handoff**: The extracted text is processed by a multi-agent orchestrator that generates a structured portfolio JSON.
4.  **Validation**: Every AI output is strictly validated against a **Pydantic Schema** (Contract) before being saved to the database to prevent hallucinations or malformed payloads.

[Image of a background task lifecycle showing the steps of ingestion, processing, validation, and storage]

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* PostgreSQL Database
* Firebase Service Account Key (`.json`)
* Google AI Studio API Key (Gemini)

### 2. Installation
```bash
git clone [https://github.com/your-username/showcase-ai-backend.git](https://github.com/your-username/showcase-ai-backend.git)
cd showcase-ai-backend
pip install -r requirements.txt

## ⚙️ Configuration & Environment

The application uses **Pydantic Settings** to manage environment variables. Create a `.env` file in the root directory to store your credentials:

```bash
# Environment
ENV=development
SECRET_KEY=yoursecretkeyhere_min_32_chars

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/showcase_db

# Firebase Auth
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json

# Google Gemini AI
GEMINI_API_KEY=your_google_gemini_key
GEMINI_VISION_MODEL=gemini-1.5-flash
GEMINI_AGENT_MODEL=gemini-1.5-pro

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

### Running the Server
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server with auto-reload for development
uvicorn app.main:app --reload


🛣️ API EndpointsThe API is versioned under /api/v1 to follow industry-standard REST practices.📄 Resume ManagementMethodEndpointDescriptionAuthPOST/api/v1/resume/uploadValidates file and triggers background AI pipeline.✅ Firebase🎨 Portfolio ManagementMethodEndpointDescriptionAuthGET/api/v1/portfolio/meFetches all portfolios owned by the logged-in user.✅ FirebaseGET/api/v1/portfolio/{job_id}Fetches detailed private portfolio data.✅ FirebasePATCH/api/v1/portfolio/{job_id}/publishToggles visibility and sets a custom URL slug.✅ FirebaseGET/api/v1/portfolio/public/{slug}Public Gateway: Accessible by anyone via unique link.❌ Public🏥 System HealthMethodEndpointDescriptionAuthGET/healthReturns service status, version, and auth engine.❌ Public
