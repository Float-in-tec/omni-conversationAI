from pydantic import BaseModel, ConfigDict

class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    model_config = ConfigDict(from_attributes=True)
