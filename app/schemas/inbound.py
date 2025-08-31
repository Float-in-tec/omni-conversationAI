from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class InboundMessageIn(BaseModel):
    company_id: int
    channel_id: int
    from_: str = Field(alias="from")
    text: str
    channel_message_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
