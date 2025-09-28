from enum import Enum

class ResponseSignal(Enum):
    ERROR_PAGE_ID_NOT_FOUND = "Page Id Not Found"
    ERROR_ACCESS_TOKEN_NOT_FOUND = "Access Token Not Found"
    ERROR_RESPONSE_TOKEN_NOT_FOUND = "Response Token Not Found"
    ERROR_POST_UPLOAD_FAILED = "post upload failed"
    
    SUCCESS_POST_UPLOAD = "post upload successfully uploaded"
