from typing import Optional
from sqlalchemy.orm import Session
from app.dao.company import DAOCompany
from app.dao.channel import DAOChannel
from app.dao.users import DAOUser
from app.dao.contact import DAOContact
from app.dao.conversation import DAOConversation
from app.dao.message import DAOMessage




def get_or_create_company(db: Session, company_id: int) -> DAOCompany:
    company = db.query(DAOCompany).filter(DAOCompany.id == company_id).first()
    if not company:
        company = DAOCompany(id=company_id, name=f"Company {company_id}")
        db.add(company)
        db.commit()
    return company

def get_or_create_channel(db: Session, company_id: int, channel_id: int) -> DAOChannel:
    ch = db.query(DAOChannel).filter(DAOChannel.id == channel_id).first()
    if not ch:
        ch = DAOChannel(id=channel_id, company_id=company_id, name=f"channel-{channel_id}", type="whatsapp")
        db.add(ch)
        db.commit()
    return ch

def get_or_create_ai_user(db: Session, company_id: int) -> DAOUser:
    bot = db.query(DAOUser).filter(DAOUser.company_id == company_id, DAOUser.role == "ai").first()
    if not bot:
        bot = DAOUser(company_id=company_id, name="AI Bot", role="ai")
        db.add(bot)
        db.commit()
        db.refresh(bot)
    return bot

def get_or_create_default_agent(db: Session, company_id: int) -> DAOUser:
    """
    Returns a default human agent for the company. Creates one if missing.
    """
    agent = (db.query(DAOUser)
              .filter(DAOUser.company_id == company_id, DAOUser.role == "agent")
              .order_by(DAOUser.id.asc())
              .first())
    if not agent:
        agent = DAOUser(company_id=company_id, name="Default Agent", role="agent")
        db.add(agent)
        db.commit()
        db.refresh(agent)
    return agent

def get_or_create_contact_by_phone(db: Session, company_id: int, phone: str) -> DAOContact:
    contact = db.query(DAOContact).filter(DAOContact.company_id == company_id, DAOContact.phone == phone).first()
    if not contact:
        contact = DAOContact(company_id=company_id, phone=phone, name=None, email=None)
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact

def find_open_conversation(db: Session, company_id: int, channel_id: int, contact_id: int) -> Optional[DAOConversation]:
    return (db.query(DAOConversation)
              .filter(DAOConversation.company_id == company_id,
                      DAOConversation.channel_id == channel_id,
                      DAOConversation.contact_id == contact_id)
              .order_by(DAOConversation.id.desc())
              .first())

def create_conversation(db: Session, company_id: int, channel_id: int, contact_id: int, owner_id: Optional[int]) -> DAOConversation:
    conv = DAOConversation(company_id=company_id, channel_id=channel_id, contact_id=contact_id, owner_id=owner_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def add_message(db: Session, conversation_id: int, sender: str, content: str) -> DAOMessage:
    msg = DAOMessage(conversation_id=conversation_id, sender=sender, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def add_ai_autoreply(db: Session, conversation: DAOConversation, inbound_text: str) -> DAOMessage:
    """
    Deterministic mock AI reply. No external calls.
    """
    company = db.query(DAOCompany).filter(DAOCompany.id == conversation.company_id).first()
    brand = f" ({company.name})" if company and company.name else ""
    content = f"Auto-reply from AI bot{brand}: I received your message: '{inbound_text}'"
    msg = DAOMessage(conversation_id=conversation.id, sender="ai", content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def toggle_conversation_owner(db: Session, conversation: DAOConversation) -> str:
    """
    If current owner is AI -> switch to human (auto-create default agent).
    If current owner is human/agent -> switch to AI.
    Returns the new role string: "human" or "ai".
    """
    # figure out current role
    cur_role = None
    if conversation.owner_id:
        owner = db.query(DAOUser).filter(DAOUser.id == conversation.owner_id).first()
        cur_role = owner.role if owner else None

    if cur_role == "agent":
        # switch to AI
        bot = get_or_create_ai_user(db, conversation.company_id)
        conversation.owner_id = bot.id
        db.commit()
        return "ai"
    else:
        # switch to human
        agent = get_or_create_default_agent(db, conversation.company_id)
        conversation.owner_id = agent.id
        db.commit()
        return "human"
