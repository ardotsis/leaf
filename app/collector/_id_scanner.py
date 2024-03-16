import asyncio
from logging import getLogger
from pathlib import Path

from bs4 import BeautifulSoup

from app import _custom_httpx
from app.collector._exceptions import (InvalidPageRangeError,
                                       InvalidResourceFormatError)

_logger = getLogger(__name__)
_RESOURCE_FILE = Path(__file__).parent / "resource_url.txt"

Httpx = _custom_httpx.get()


def _get_resource_url() -> str:
    with open(_RESOURCE_FILE, "r", encoding="utf-8") as f:
        resource_url = f.read().strip()

    if "{}" not in resource_url:
        raise InvalidResourceFormatError

    return resource_url


async def _get_product_urls(products_url: str) -> list[str]:
    r = await Httpx.get(products_url)
    soup = BeautifulSoup(r.text, "html.parser")

    urls = []
    for product in soup.find_all(class_="multiline_truncate"):
        urls.append(product.find_next().get("href"))

    return urls


def _extract_id(product_url: str) -> str:
    return product_url.split("/")[-1].split(".")[0]


async def gets(from_: int, to: int) -> list[str]:
    if (from_ <= 0 or to <= 0) or (from_ > to):
        raise InvalidPageRangeError

    resource_url = _get_resource_url()

    jobs = []
    for page_num in range(from_, to + 1):
        products_url = resource_url.format(page_num)
        job = _get_product_urls(products_url)
        jobs.append(job)

    product_ids = []
    for product_urls in await asyncio.gather(*jobs):
        for product_url in product_urls:
            product_ids.append(_extract_id(product_url))

    return product_ids
