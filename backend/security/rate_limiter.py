from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def _real_ip(request: Request) -> str:
    # Render (and most proxies) set X-Forwarded-For with the real client IP
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    # fallback for local dev
    return get_remote_address(request) or '127.0.0.1'


limiter = Limiter(key_func=_real_ip)
