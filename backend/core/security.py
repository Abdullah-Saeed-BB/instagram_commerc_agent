import hashlib
import hmac

from fastapi import HTTPException, Request, status

from core.config import get_settings


async def verify_webhook_signature(request: Request) -> bytes:
    """
    Validate the X-Hub-Signature-256 header that Meta sends on every
    webhook POST.  Raises HTTP 403 on any failure.
    Returns the raw request body so the caller doesn't have to read it twice.
    """
    settings = get_settings()
    signature_header: str = request.headers.get("X-Hub-Signature-256", "")
    body: bytes = await request.body()

    if not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or malformed X-Hub-Signature-256 header.",
        )

    received_sig = signature_header[len("sha256="):]
    expected_sig = hmac.new(
        settings.META_APP_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(received_sig, expected_sig):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Webhook signature verification failed.",
        )

    return body
