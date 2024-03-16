import asyncio
import logging
from argparse import ArgumentParser, Namespace

from bs4 import BeautifulSoup

from app import custom_httpx
from app.dlsite import id_scanner
from app.dlsite.fetcher import Fetcher
from app.models import Product

_logger = logging.getLogger(__package__)


def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-frm", type=int, default=1)
    parser.add_argument("-to", type=int, required=True)
    args = parser.parse_args()
    return args


async def fetch_product(product_id: str) -> Product:
    fetcher = Fetcher(product_id)
    product_page = await fetcher.get_product_page()
    page_soup = BeautifulSoup(product_page, "html.parser")
    product = Product(
        product_id,
        fetcher.get_work_name(page_soup),
        fetcher.url,
        await fetcher.get_voice_actors(page_soup),
        fetcher.get_trial_url(page_soup),
        await fetcher.get_chobit_urls(),
    )
    return product


async def main() -> None:
    args = get_args()

    _logger.info(f"Process 1 Scan product IDs ({args.frm} <-> {args.to})")
    ids = await id_scanner.gets(args.frm, args.to)

    _logger.info("Process 2 - Fetch product pages")
    fetch_jobs = []
    for id_ in ids:
        fetch_job = fetch_product(id_)
        fetch_jobs.append(fetch_job)

    await asyncio.gather(*fetch_jobs)


async def runner() -> None:
    try:
        await main()
    finally:
        _logger.debug("Closing custom httpx instance...")
        await custom_httpx.get().aclose()


if __name__ == "__main__":
    asyncio.run(runner())
