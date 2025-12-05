import time
import logging
from fastapi import Request
from src.helpers.logging_config import setup_logger

logger = logging.getLogger("request")

async def log_requests(request: Request, call_next):

    start = time.time()

    logger.info(f"==> {request.method} {request.url.path}")

    response = await call_next(request)

    processing_time = (time.time() - start) * 1000  # ms with full precision

    logger.info(
        f"<== {response.status_code} | {request.method} {request.url.path} "
        f"| {processing_time} ms"
    )

    return response
