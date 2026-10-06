import json
import logging
import os
import time

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.triage import classify_email


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record),
        }
        return json.dumps(log_data)


logger = logging.getLogger("email_triage")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

if not logger.handlers:
    logger.addHandler(handler)


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Brew & Bean Email Triage API",
    version="1.0.0",
)

app.state.limiter = limiter


class TriageRequest(BaseModel):
    email_text: str


class TriageResponse(BaseModel):
    category: str
    confidence: float


def verify_token(x_auth_token: str | None = Header(default=None)):
    expected_token = os.getenv("AUTH_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="AUTH_TOKEN is not configured",
        )

    if x_auth_token != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    return True


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded,
):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post(
    "/triage",
    response_model=TriageResponse,
)
@limiter.limit("10/minute")
async def triage(
    request: Request,
    data: TriageRequest,
    authenticated: bool = Depends(verify_token),
):
    start_time = time.perf_counter()

    result = classify_email(data.email_text)

    elapsed = time.perf_counter() - start_time

    logger.info(
        "Email classified: category=%s confidence=%s latency_ms=%.2f",
        result["category"],
        result["confidence"],
        elapsed * 1000,
    )

    return result