import httpx
from httpx import Timeout

_client = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=14, max_connections=14),
    timeout=Timeout(timeout=10.0, pool=None),
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    },
)


def get() -> httpx.AsyncClient:
    return _client
