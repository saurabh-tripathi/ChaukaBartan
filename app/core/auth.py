import hashlib
import hmac

from app.core.config import get_settings

_MSG = b"cb_valid_session"


def make_session_token() -> str:
    key = get_settings().SECRET_KEY.encode()
    return hmac.new(key, _MSG, hashlib.sha256).hexdigest()


def verify_session_token(token: str | None) -> bool:
    if not token:
        return False
    return hmac.compare_digest(token, make_session_token())
