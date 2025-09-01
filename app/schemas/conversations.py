from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal

class ConversationOut(BaseModel):
    id: int
    company_id: int
    channel_id: int
    contact_id: int
    owner_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class AgentMessageIn(BaseModel):
    author_id: int
    text: str
