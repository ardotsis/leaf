import httpx

_client = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=8, max_connections=8),
    timeout=10.0,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    },
)


def get() -> httpx.AsyncClient:
    return _client
