# Sailer Core – Backend Developer Challenge

## 📌 Overview
This project is my implementation of the **Sailer AI Backend Developer Challenge**.  
It simulates the **core backend service** of an omnichannel, multi-tenant conversational platform.  
The service is built with **FastAPI**, **MySQL**, **SQLAlchemy**, **Celery**, and **Redis**, and is containerized with **Docker Compose** for easy setup.

### Key Features
- **Multi-tenancy** – all data is isolated by `company_id`.  
- **Multi-channel** – each company can have multiple channels (WhatsApp, Email, etc.).  
- **Conversations & Messages** – track conversations between contacts and agents/AI.  
- **Contacts** – store basic contact info + custom fields.  
- **Multi-participant & Transfers** – transfer ownership between AI and human agents.  
- **AI Integration (mocked)** – simple logic: new conversations start with an AI bot.  
- **Bonus** – automatic contact data extraction from messages (e.g., detect name & email).  

---

## 🏗️ Architecture

This project follows an **MVC-inspired architecture**, consistent with previous projects I’ve worked on:

- **DAO (Models)** → SQLAlchemy ORM classes that map to DB tables.  
- **DB Utils** → connection/session manager for MySQL.  
- **Services (Controllers)** → business logic (conversation lifecycle, routing, AI).  
- **REST API (Views)** → FastAPI endpoints, focused only on request/response handling.  
- **SQL Folder** → `.sql` migration files to initialize or evolve schema.  
- **Celery Workers** → async tasks for AI calls and background processing.  

```
sailer-core/
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ sql/
│   └─ 001_init.sql          # DB schema initialization
├─ app/
│  ├─ rest_api/              # REST API endpoints (Views)
│  ├─ dao/                   # SQLAlchemy models (DAO layer)
│  ├─ services/              # Business logic (Controllers)
│  ├─ db_utils/              # DB connection/session utils
│  ├─ tests/                 # Unit + integration tests
│  └─ main.py                # FastAPI app entrypoint
└─ README.md
```

---

## 🗄️ Data Models

All entities are **scoped by `company_id`** for tenant isolation.

### Company
- `id` (PK, uuid)  
- `name` (str)  

### Channel
- `id` (PK, uuid)  
- `company_id` (FK → Company)  
- `provider` (e.g. `whatsapp`, `email`)  
- `external_id` (e.g. phone number, email)  

### Contact
- `id` (PK, uuid)  
- `company_id` (FK → Company)  
- `external_id` (per-channel identifier, e.g. phone/email)  
- `name`, `email`, `phone`  
- `custom_fields` (JSON, optional)  

### User (Agent / AI)
- `id` (PK, uuid)  
- `company_id`  
- `name`  
- `role` (`agent`, `admin`, `ai-bot`)  
- `is_bot` (bool)  

### Conversation
- `id` (PK, uuid)  
- `company_id`  
- `channel_id`  
- `contact_id`  
- `owner_id` (FK → User)  
- `created_at`, `updated_at`  

### Message
- `id` (PK, uuid)  
- `company_id`  
- `conversation_id`  
- `contact_id` (nullable, if agent/AI sent it)  
- `author_id` (nullable, if contact sent it)  
- `direction` (`inbound` | `outbound`)  
- `channel_message_id` (unique per channel)  
- `text`, `attachments (JSON)`  
- `created_at`  
- `processed_by_ai` (bool)  

---

## 🌐 API Endpoints

### Inbound
`POST /webhooks/inbound`  
Receive a new inbound message.  
- Body: `{ company_id, channel_id, from, text, channel_message_id }`  
- Behavior:  
  1. Find/create `Contact`.  
  2. Find/create `Conversation`.  
  3. Create inbound `Message`.  
  4. Assign owner (AI if new conversation).  
  5. Trigger Celery task → mocked AI response.  

### Conversations
- `GET /conversations/{conversation_id}` – Retrieve conversation + messages.  
- `POST /conversations/{conversation_id}/messages` – Agent sends outbound message.  
- `POST /conversations/{conversation_id}/transfer` – Transfer ownership to another user.  
- `GET /companies/{company_id}/conversations` – List conversations (filter by owner/channel).  

### Contacts
- `POST /contacts/{contact_id}/custom-fields` – Update custom fields.  

### Companies
- `POST /companies` – Create company (creates default AI bot user).  

### Health
- `GET /health` – Readiness check.  

---

## ⚙️ Setup Instructions

### Requirements
- Docker & Docker Compose installed.  

### Run
```bash
# Start the full stack (FastAPI, MySQL, Redis, Celery)
docker-compose up --build
```

API will be available at:  
👉 `http://localhost:8000/docs` (Swagger UI)

---

## 📖 Example Usage

### 1. Inbound message
```bash
curl -X POST http://localhost:8000/webhooks/inbound   -H "Content-Type: application/json"   -d '{
    "company_id": "company-123",
    "channel_id": "whatsapp-1",
    "channel_message_id": "msg-001",
    "from": "+5511999888777",
    "text": "Hi, my name is Alex and my email is alex@example.com"
  }'
```

### 2. Retrieve conversation
```bash
curl http://localhost:8000/conversations/{conversation_id}
```

### 3. Agent replies
```bash
curl -X POST http://localhost:8000/conversations/{conversation_id}/messages   -H "Content-Type: application/json"   -d '{"author_id":"agent-1","text":"Hello Alex, how can I help?"}'
```

### 4. Transfer to human
```bash
curl -X POST http://localhost:8000/conversations/{conversation_id}/transfer   -H "Content-Type: application/json"   -d '{"new_owner_id":"agent-2"}'
```

---

## 🧠 AI Integration (Mocked)

- New conversations → assigned to AI bot (`is_bot=True`).  
- Mocked AI Celery task generates a simple auto-reply after a delay.  
- **Bonus:** If message contains `"my name is X"` or `"my email is Y"`, service extracts values and updates `Contact` automatically.  

---

## 🧪 Testing

We use both **pytest** and **unittest**:
- **pytest** for async integration tests (`httpx.AsyncClient` against FastAPI).  
- **unittest.TestCase** for DAO + DB utils tests.  

Run tests:
```bash
# Using pytest
pytest

# Or using unittest
python -m unittest discover -s app/tests
```

---

## 🛠️ Design Rationale

- **Database (DB)**: MySQL chosen for familiarity and JSON field support.  
- **DB schema and migrations**: managed with `.sql` files in `sql/` (clear, explicit, consistent with prior work).  
- **Architecture**: MVC-like separation (DAO, Services, REST API).  
- **Async tasks**: Celery + Redis to simulate scalable async processing.  
- **Testing**: mix of pytest and unittest to balance modern async testing with traditional familiarity.  
- **AI**: mocked service keeps setup simple and reproducible, but is pluggable for future Hugging Face/OpenAI backends.  
- **Multi-tenancy design choice**:  
  In this implementation, tenant isolation is achieved by scoping all tables with a `company_id` column.  
  For production systems requiring stricter isolation, one could adopt either:
    - Schema-per-tenant (separate schemas in the same DB)  
    - Database-per-tenant (physically separate databases)  
  We use the `company_id` scoping approach here for simplicity and faster iteration. It is pragmatic for this coding challenge while still demonstrating the principle of multi-tenancy.

---

## 🚀 Next Steps (Future Improvements)
- Add real channel connectors (WhatsApp, Email).  
- Add authentication + JWT for agents.  
- Implement retries/dead-letter queues for failed AI tasks.  
- Expand AI logic to use real NLP models.  
