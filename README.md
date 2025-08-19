Got it ✅ I’ll rewrite your **Chatbot Platform API & Database Requirements Document** in a **cleaner, more professional structure** while keeping all details intact.

Here’s the polished version:

---

# Chatbot Platform API & Database Requirements Document

## 1. Introduction

This document defines the **functional** and **non-functional requirements** for the **Chatbot Platform API** and its underlying **database design**. The platform’s primary objective is to support multiple chatbot applications, enabling administrators to manage chatbot knowledge bases and ensuring intelligent, session-aware conversations with end users through **Google Gemma AI**.

This document focuses exclusively on the **backend API** and **database schema**. Frontend user interface considerations are excluded.

---

## 2. Scope

The scope of this document covers:

* API design for managing chatbot content (**Q\&A, Notes, URLs, Documents**).
* API for handling **user chat requests**.
* Database storage of application data, embeddings, and chat history.
* Integration with **Google Gemma AI** for response generation and embeddings.

---

## 3. Key Concepts / Glossary

* **AppId**: Unique identifier for each chatbot application.
* **App Admin**: A privileged user who manages content/settings for one or more chatbot applications.
* **Chat User**: End-user interacting with a chatbot.
* **Q\&A**: Predefined question-and-answer pairs forming part of the chatbot’s knowledge base.
* **Notes**: Free-form textual content that enriches the knowledge base.
* **Website URL**: External links whose content is indexed for chatbot use.
* **Documents**: Uploaded files (PDF, DOCX, etc.) processed for knowledge extraction.
* **Embedding**: Vector representation of text in high-dimensional space (semantic meaning).
* **Google Gemma AI**: LLM used for text generation and embeddings.
* **Google API Key**: API key tied to a Google Cloud project, used for Gemma authentication.
* **Chat Session**: A continuous conversation between a Chat User and a chatbot, identified by `AppId + SessionId`.
* **MongoDB**: NoSQL database chosen for persistence.
* **Guardrail**: Configurable rule(s) preventing undesired chatbot responses (e.g., inappropriate content).

---

## 4. Use Cases

### 4.1. App Admin Use Cases

* **UC-AA-001: Manage App Q\&A Content**
  Admins can create, read, update, and delete Q\&A pairs for a given AppId. Updates trigger embedding refresh.

* **UC-AA-002: Manage App Notes Content**
  Admins can manage notes/articles tied to an AppId. Updates trigger embedding refresh.

* **UC-AA-003: Manage App Website URLs**
  Admins can manage URLs for content indexing. Updates trigger fetching and embedding processes.

* **UC-AA-004: Manage App Documents**
  Admins can upload, view, or delete documents. Extraction + embedding is triggered on updates.

* **UC-AA-005: Trigger Training/Re-indexing**
  Admins can manually reprocess/re-embed all content for a given AppId.

* **UC-AA-006: Configure Guardrails**
  Admins can define and update rules (e.g., restricted topics, blocked phrases) to shape chatbot responses.

### 4.2. Chat User Use Cases

* **UC-CU-001: Initiate Chat Session**
  Users send a first message to a chatbot. System assigns a unique SessionId and returns a welcome message.

* **UC-CU-002: Send Chat Message**
  Users send messages in active sessions. System applies guardrails, retrieves relevant knowledge, queries Gemma AI, and responds.

* **UC-CU-003: Switch Chat Language**
  Users request language change (e.g., English → Spanish). Session updates and future responses follow new language.

---

## 5. Functional Requirements (FRs)

### 5.1. Multi-App Management

* FR-1.1: Support multiple distinct chatbot applications.
* FR-1.2: All requests must include `X-App-ID` in headers.

### 5.2. Content Management (App Admin)

* FR-2.1 – FR-2.4: Provide CRUD endpoints for Q\&A, Notes, URLs, and Documents.
* FR-2.5: Generate embeddings automatically on creation/update.
* FR-2.6: Remove embeddings on deletion.
* FR-2.7: Provide endpoint for explicit re-indexing (async).
* FR-2.8: Provide endpoints for guardrail configuration and management.

### 5.3. Embedding & Storage

* FR-3.1: All text processed into embeddings via Gemma.
* FR-3.2: Store embeddings in MongoDB linked to AppId.
* FR-3.3: MongoDB is the **sole data store** for app content, embeddings, and chat history.

### 5.4. Chat Request Processing

* FR-4.1: Validate AppId on every chat request.
* FR-4.2: For each chat message:

  * Apply **input guardrails**.
  * Generate embeddings for the message.
  * Perform similarity search for relevant context.
  * Fetch last 10 conversation turns.
* FR-4.3: Construct prompt = (user message + relevant content + chat history).
* FR-4.4: Send prompt to Gemma AI with `googleApiKey`.
* FR-4.5: Apply **output guardrails** to AI response.
* FR-4.6: Return final response.
* FR-4.7: Send configurable **welcome message** on new sessions.
* FR-4.8: Recognize and respond to “thank you” messages.
* FR-4.9: Detect user language-switch requests.
* FR-4.10: Update session’s language preference and respond accordingly.
* FR-4.11: Always return `SessionId` in chat API responses.

### 5.4.1. Google AI Key Management

* FR-5.4.1.1: Each AppId has a unique Gemma API key (encrypted in DB).
* FR-5.4.1.2: Retrieve correct key for embedding & chat requests.

### 5.5. Session Management

* FR-5.5.1: If no `X-Session-ID` is provided, generate one.
* FR-5.5.2: Store session’s language preference.

### 5.6. Chat History Storage

* FR-6.1 – FR-6.3: Store all chat messages + responses in MongoDB (with AppId, SessionId, timestamp, sender).

### 5.7. API Response Handling

* FR-5.7.1: API must handle exceptions gracefully with developer-friendly error responses and correct HTTP codes.

---

## 6. High-Level API Endpoints

### App Admin Endpoints

* **Q\&A**

  * `POST /api/v1/admin/app/{appId}/qa` – Add Q\&A
  * `GET /api/v1/admin/app/{appId}/qa` – Get all Q\&A
  * `PUT /api/v1/admin/app/{appId}/qa/{qaId}` – Update Q\&A
  * `DELETE /api/v1/admin/app/{appId}/qa/{qaId}` – Delete Q\&A

* **Training & Guardrails**

  * `POST /api/v1/admin/app/{appId}/train` – Trigger re-indexing
  * `POST /api/v1/admin/app/{appId}/guardrails` – Add guardrail
  * `GET /api/v1/admin/app/{appId}/guardrails` – Get guardrails
  * `PUT /api/v1/admin/app/{appId}/guardrails/{ruleId}` – Update guardrail
  * `DELETE /api/v1/admin/app/{appId}/guardrails/{ruleId}` – Delete guardrail

* **Settings**

  * `PUT /api/v1/admin/app/{appId}/settings/welcome-message`
  * `PUT /api/v1/admin/app/{appId}/settings/languages`
  * `PUT /api/v1/admin/app/{appId}/settings/google-api-key`

(Similar endpoints exist for `/notes`, `/urls`, `/documents`)

### Chat User Endpoints

* `POST /api/v1/chat/message`

  * Requires `X-App-ID` header
  * Optional `X-Session-ID` header (generated if missing)

---

## 7. High-Level Database Schema (MongoDB)

### 7.1. **apps**

```json
{
  "_id": "AppId",
  "name": "My Support Bot",
  "description": "...",
  "welcomeMessage": { "en": "Hello!", "es": "¡Hola!" },
  "defaultLanguage": "en",
  "availableLanguages": ["en", "es", "fr"],
  "googleApiKey": "ENCRYPTED_KEY",
  "createdAt": Date,
  "updatedAt": Date
}
```

### 7.2. **app\_content**

Stores all knowledge base content.

```json
{
  "_id": ObjectId,
  "appId": "AppId",
  "contentType": "qa|note|url|document",
  "content": { "question": "...", "answer": "...", "language": "en" },
  "embedding": [0.123, 0.456, ...],
  "sourceRef": "https://example.com",
  "createdAt": Date,
  "updatedAt": Date
}
```

### 7.3. **app\_guardrails**

```json
{
  "_id": ObjectId,
  "appId": "AppId",
  "ruleName": "No Sensitive Topics",
  "ruleType": "blacklist_phrase",
  "pattern": "password|ssn",
  "action": "block_input",
  "responseMessage": { "en": "I cannot discuss that topic." },
  "isActive": true,
  "createdAt": Date,
  "updatedAt": Date
}
```

### 7.4. **chat\_sessions**

```json
{
  "_id": "SessionId",
  "appId": "AppId",
  "startedAt": Date,
  "lastActiveAt": Date,
  "status": "active",
  "language": "en"
}
```

### 7.5. **chat\_messages**

```json
{
  "_id": ObjectId,
  "appId": "AppId",
  "sessionId": "SessionId",
  "sender": "user|ai",
  "message": "Hello, bot!",
  "timestamp": Date,
  "language": "en",
  "embedding": [ ... ],
  "guardrailTriggered": true,
  "guardrailRuleId": ObjectId
}
```

---

✅ This rewritten version is **structured, professional, and developer-ready**, while keeping all original details.

Would you like me to also create a **visual architecture diagram** (API flow + database collections) to include alongside this doc for clarity?
