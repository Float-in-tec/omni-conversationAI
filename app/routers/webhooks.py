# app/routers/webhooks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db_utils.deps import get_db
from app.schemas.inbound import InboundMessageIn
from app.schemas.conversations import ConversationOut
from app.services.conversation import (
    get_or_create_company,
    get_or_create_channel,
    get_or_create_contact_by_phone,
    get_or_create_ai_user,
    find_open_conversation,
    create_conversation,
    add_message,
    add_ai_autoreply,  # <-- mock reply
)

router = APIRouter()

@router.post("/webhooks/inbound", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def inbound_webhook(payload: InboundMessageIn, db: Session = Depends(get_db)):
    # 1) ensure company/channel/contact exist
    company = get_or_create_company(db, payload.company_id)
    channel = get_or_create_channel(db, company_id=company.id, channel_id=payload.channel_id)
    contact = get_or_create_contact_by_phone(db, company_id=company.id, phone=payload.from_)

    # 2) ensure an AI-bot owner exists (role="ai")
    ai_user = get_or_create_ai_user(db, company_id=company.id)

    # 3) find existing conversation or create a new one
    conv = find_open_conversation(db, company_id=company.id, channel_id=channel.id, contact_id=contact.id)
    if not conv:
        conv = create_conversation(db, company_id=company.id, channel_id=channel.id, contact_id=contact.id, owner_id=ai_user.id)

    # 4) add inbound message (from contact)
    add_message(db, conversation_id=conv.id, sender="contact", content=payload.text)

    # 5) mock AI auto-reply (no network calls, always succeeds)
    if conv.owner_id == ai_user.id:
        add_ai_autoreply(db, conversation=conv, inbound_text=payload.text)

    # 6) return conversation summary
    return ConversationOut(
        id=conv.id,
        company_id=conv.company_id,
        channel_id=conv.channel_id,
        contact_id=conv.contact_id,
        owner_id=conv.owner_id,
    )
