from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db_utils.deps import get_db
from app.dao.conversation import DAOConversation
from app.dao.users import DAOUser
from app.dao.message import DAOMessage
from app.schemas.conversations import ConversationOut, AgentMessageIn, TransferIn
from app.schemas.messages import MessageOut
from app.services.conversation import add_message

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(DAOConversation).filter(DAOConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

from app.dao.message import DAOMessage

@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
def list_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(DAOConversation).filter(DAOConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    rows = (db.query(DAOMessage)
              .filter(DAOMessage.conversation_id == conversation_id)
              .order_by(DAOMessage.id.asc())
              .all())
    # returning extra info in response for easier use of endpoints
    return [{"id": m.id, "conversation_id": m.conversation_id, "sender": m.sender, "content": m.content}
            for m in rows]

@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def agent_send_message(conversation_id: int, payload: AgentMessageIn, db: Session = Depends(get_db)):
    conv = db.query(DAOConversation).filter(DAOConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user = db.query(DAOUser).filter(DAOUser.id == payload.author_id, DAOUser.company_id == conv.company_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Author (agent) not found for this company")

    msg = add_message(db, conversation_id=conversation_id, sender="agent", content=payload.text)
    # return as dict to satisfy MessageOut without relying on from_attributes
    return {"id": msg.id, "conversation_id": msg.conversation_id, "sender": msg.sender, "content": msg.content}

@router.post("/{conversation_id}/transfer", status_code=status.HTTP_204_NO_CONTENT)
def transfer_conversation(conversation_id: int, payload: TransferIn, db: Session = Depends(get_db)):
    conv = db.query(DAOConversation).filter(DAOConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    new_owner = db.query(DAOUser).filter(DAOUser.id == payload.new_owner_id, DAOUser.company_id == conv.company_id).first()
    if not new_owner:
        raise HTTPException(status_code=400, detail="New owner not found for this company")

    conv.owner_id = new_owner.id
    db.commit()
    return
