from enum import Enum

class ResponseSignal(Enum):
    ERROR_PAGE_ID_NOT_FOUND = "Page Id Not Found"
    ERROR_ACCESS_TOKEN_NOT_FOUND = "Access Token Not Found"
    ERROR_RESPONSE_TOKEN_NOT_FOUND = "Response Token Not Found"
    ERROR_POST_UPLOAD_FAILED = "post upload failed"
    ERROR_POST_UPDATED_FAILED = "post updated failed"
    
    SUCCESS_POST_UPLOAD = "post upload successfully uploaded"
    UPADTED_POST_SCCESS = "post update sucessfully"

    DRAFT_NOT_FOUND="Draft not found"
    ACCEPTED_POST_NOT_FOUND= "No accepted posts found"
    REJECTED_POST_NOT_FOUND= "No rejected posts found"

    INVALID_USER_ID ="Invalid user_id format"
    FAILED_TO_MARK_AS_READ = "Failed to mark notification as read"
    NOTIFICATION_NOT_FOUND = "Notification not found."
