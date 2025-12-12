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
    
    ERROR_USER_IS_ALREADY_EXIST = "error user is already exist"
    USER_REGISTERED_SUCCESSFULLY= "User registered successfully"

    RECOMMENDATION_NOT_FOUND = "Recommendation not found"
    COMPETITOR_ANALYSIS_NOT_FOUND = "Competitor analysis not found"
    INTERACTION_ANALYSIS_NOT_FOUND = "Interaction analysis not found"

    BUSINESS_INFO_CREATED = "Business Info created successfully"
    BUSINESS_INFO_UPDATED = "Business Info updated successfully"
    BUSINESS_INFO_NOT_FOUND = "Business Info not found"
    BUSINESS_INFO_ALREADY_EXISTS = "Business Info already exists"
    FACEBOOK_CREDENTIALS_UPDATED = "Facebook credentials updated successfully"
