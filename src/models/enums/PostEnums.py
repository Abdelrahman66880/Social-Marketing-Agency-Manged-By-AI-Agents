from enum import Enum

class PostStatus(str, Enum):
    DRAFT = "draft"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

