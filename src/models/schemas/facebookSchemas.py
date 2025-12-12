
# src/schemas/facebook.py
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict

# =====================
# REQUEST MODELS
# =====================

class FacebookReplyRequest(BaseModel):
    recipient: Dict[str, str] = Field(..., description="PSID (Page-scoped user ID)")
    message: Optional[Dict[str, str]] = Field(None, description="Text of the message (UTF-8, <2000 chars)")
    messaging_type: Literal["RESPONSE", "UPDATE", "MESSAGE_TAG"] = "RESPONSE"
    notification_type: Optional[Literal["NO_PUSH", "REGULAR", "SILENT_PUSH"]] = "REGULAR"
    tag: Optional[
        Literal[
            "ACCOUNT_UPDATE",
            "CONFIRMED_EVENT_UPDATE",
            "CUSTOMER_FEEDBACK",
            "HUMAN_AGENT",
            "POST_PURCHASE_UPDATE",
        ]
    ] = None
    reply_to: Optional[dict] = None  # {"mid": "<message_id>"}

class ReplyMessageRequest(BaseModel):
    reply_text: str = Field(..., description="Text content of the reply")
    message_type: str = Field("RESPONSE", description="Messaging type (RESPONSE, UPDATE, MESSAGE_TAG)")


class ReplyCommentRequest(BaseModel):
    reply: str = Field(..., description="Reply text")
