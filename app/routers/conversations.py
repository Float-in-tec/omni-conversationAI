from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db_utils.deps import get_db
from app.dao.conversation import DAOConversation
from app.dao.users import DAOUser
from app.dao.message import DAOMessage
from app.schemas.conversations import ConversationOut, AgentMessageIn
from app.schemas.messages import MessageOut
from app.services.conversation import add_message, toggle_conversation_owner


router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(DAOConversation).filter(DAOConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


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

@router.post("/{conversation_id}/transfer-toggle")
def transfer_toggle(conversation_id: int, db: Session = Depends(get_db)):
    """
    Toggle ownership between AI and a human agent.
    - If owner is AI -> switch to human (auto-creates a default agent if needed)
    - If owner is human -> switch to AI
    """
    conv = db.query(DAOConversation).filter(DAOConversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    new_role = toggle_conversation_owner(db, conv)
    return {"detail": f"switched ownership to {new_role}"}
