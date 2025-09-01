import json
import sys, os
from fastapi.testclient import TestClient


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from app.main import app


client = TestClient(app)

def test_inbound_creates_conversation_and_ai_reply():
    payload = {
        "company_id": 1,
        "channel_id": 1,
        "from": "+15550009999",
        "text": "hello from test",
        "channel_message_id": "test-001"
    }
    r = client.post("/webhooks/inbound", json=payload)
    assert r.status_code == 201
    conv = r.json()
    conv_id = conv["id"]

    r2 = client.get(f"/conversations/{conv_id}/messages")
    assert r2.status_code == 200
    msgs = r2.json()
    # Expect at least 2 messages: inbound + ai
    senders = [m["sender"] for m in msgs]
    assert "contact" in senders and "ai" in senders

def test_agent_can_send_message_and_see_it():
    # use seeded conversation 1 and seeded agent id=2
    r = client.post("/conversations/1/messages",
                    json={"author_id": 2, "text": "Taking over"})
    assert r.status_code == 201
    msg = r.json()
    assert msg["sender"] == "agent"
    assert msg["conversation_id"] == 1


def test_transfer_changes_owner():
    # Toggle should switch AI -> human (or human -> AI)
    r = client.post("/conversations/1/transfer-toggle")
    assert r.status_code == 200
    assert "switched ownership to" in r.json()["detail"]
