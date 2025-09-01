# Backend Developer Challenge
This project simulates the **core backend service** of an omnichannel, multi-tenant conversational platform.  
The service is built with **FastAPI**, **MySQL**, **SQLAlchemy**, and is containerized with **Docker Compose** for easy setup.

## Setup
For executing this apllication, you will need Docker/docker-compose installed

Tested on:
    Docker version 27.5.1 and Docker Compose version v2.22.0

1. Clone this repo into your machine
2. From project's root directory, run the following command in your terminal:
```docker-compose up -d --build```
3. (Optional) Copy `.env.example` to `.env` for setting variables and credentials:
```cp .env.example .env```
4. The API and DB should be up and running! Check API Usage and Testing for how to use the API.

## API Usage
### Endpoints
There are some seeded data so all endpoints can be tested right away.

1. POST /webhooks/inbound
Receives an inbound message from a contact, creates or continues a conversation, and adds a mock AI reply.
```
curl -s -X POST http://localhost:8000/webhooks/inbound \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "channel_id": 1,
    "from": "+15550009999",
    "text": "hello from curl",
    "channel_message_id": "demo-123"
  }' | jq
```

2. GET /conversations/{conversation_id}
Fetch conversation metadata (who owns it, which channel, which contact).
```
curl -s http://localhost:8000/conversations/1 | jq
```

3. GET /conversations/{conversation_id}/messages
Fetch all messages in a conversation (contact, AI, or agents).
```
curl -s http://localhost:8000/conversations/1/messages | jq
```

4. POST /conversations/{conversation_id}/messages
Agent sends a message into a conversation.
```
curl -s -X POST http://localhost:8000/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"author_id": 2, "text": "Hello, I am taking over"}' | jq
```

5. POST /conversations/{conversation_id}/transfer
Transfer ownership of a conversation to another agent (human agent or AI).
```
curl -i -s -X POST http://localhost:8000/conversations/1/transfer \
  -H "Content-Type: application/json" \
  -d '{"new_owner_id": 2}
```

6. POST /conversations/{conversation_id}/transfer-toggle
Toggle ownership between AI and a human agent. If a human agent doesn’t exist yet, one is created automatically.

```
curl -s -X POST http://localhost:8000/conversations/5/transfer-toggle | jq
# { "detail": "switched ownership to human" }   # or "ai"
```

### Swagger UI
Fast API allows you to visually interact with API through your browser. After containers are up, just access in your browser:
http://localhost:8000/docs

---

## Design Rationale
This project follows an **MVC-inspired architecture**, consistent with previous projects I’ve worked on:

- Data models:
  - A company has many channels, users, contacts, and conversations.
  - A conversation belongs to one company, one channel, one contact, and has an owner (user).
  - A message belongs to one conversation.
  - All entities are scoped by company_id for tenant isolation.
- Database: MySQL chosen relational consistency and ease of setup.
- Architecture:
  - DAO layer: SQLAlchemy models (map to DB tables)
  - Services: business logic (conversation lifecycle, auto-reply)
  - Routers: FastAPI endpoints (request/response only)
  - db_utils: session handling
  - sql/: schema initialization and seed data
- Async tasks: For simplicity, AI replies are mocked synchronously. Real async queue (Celery/Redis) could be added for scalability.
- Secrets: DB passwords are visible in docker-compose.yml defaults for easier review. They are not real secrets. In production, these would come from environment variables or secret managers.

## Data (Pydantic) Models:
#### Company
- id
- name
#### Channel
- id
- company_id (FK → Company)
- type (e.g. whatsapp)
#### Contact
- id
- company_id (FK → Company)
- phone, name, email
#### User
- id
- company_id
- name
- role (agent, ai)
#### Conversation
- id
- company_id
- channel_id
- contact_id
- owner_id
#### Message
- id
- conversation_id
- sender (contact, agent, ai)
- content


### Unit-tests 
A few key unit/integration tests were added (small coverage due to deadline), they can be seen in app/tests/test_flow.py
To run the tests:
```
docker-compose exec api pytest -q -W ignore::DeprecationWarning -W ignore::PendingDeprecationWarning
```

