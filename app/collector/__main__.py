import asyncio
import logging
from argparse import ArgumentParser, Namespace
from dataclasses import asdict
from datetime import datetime

from bs4 import BeautifulSoup

from app import _custom_httpx
from app._json_storage import STORAGE_DIR, JsonStorage
from app._models import Product
from app.collector import _id_scanner
from app.collector._fetcher import Fetcher

_logger = logging.getLogger(__package__)


def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-frm", type=int, default=1)
    parser.add_argument("-to", type=int, required=True)
    args = parser.parse_args()
    return args


async def get_product(product_id: str) -> Product:
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
    _logger.info(product)
    return product


async def main() -> None:
    args = get_args()

    _logger.info(f"Process 1 Scan product IDs ({args.frm} <-> {args.to})")
    ids = await _id_scanner.gets(args.frm, args.to)

    _logger.info("Process 2 - Fetch product pages")
    jobs = []
    for id_ in ids:
        job = get_product(id_)
        jobs.append(job)

    dct = {}
    for product in await asyncio.gather(*jobs):
        product_dct = asdict(product)
        product_dct.pop("id")
        dct[product.id] = product_dct

    _logger.info("Process 3 - Save dictionary data to json file")
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filepath = STORAGE_DIR / f"{date}_from_{args.frm}_to_{args.to}.json"
    storage = JsonStorage(filepath)
    storage.save(dct)


async def runner() -> None:
    try:
        await main()
    finally:
        _logger.debug("Closing custom httpx instance...")
        await _custom_httpx.get().aclose()


if __name__ == "__main__":
    asyncio.run(runner())
