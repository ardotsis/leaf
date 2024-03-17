import json
from logging import getLogger

from bs4 import BeautifulSoup

from app import _custom_httpx
from app._models import VoiceActor

_logger = getLogger(__name__)

Httpx = _custom_httpx.get()


class Fetcher:
    _cached_voice_actors: dict[str, VoiceActor] = {}

    def __init__(self, product_id: str) -> None:
        self._id = product_id

    @property
    def url(self) -> str:
        return f"https://www.dlsite.com/maniax/work/=/product_id/{self._id}.html"

    async def get_product_page(self) -> str:
        r = await Httpx.get(url=self.url)
        return r.text

    @staticmethod
    def get_work_name(product_page_soup: BeautifulSoup) -> str:
        work_name = product_page_soup.find(id="work_name").text
        return work_name

    async def get_voice_actors(
        self, product_page_soup: BeautifulSoup
    ) -> list[VoiceActor]:
        voice_actors = []
        detail_table = product_page_soup.find(id="work_outline")

        for tr in detail_table.find_all("tr"):
            title = tr.find_next("th").text
            if title == "声優":
                for voice_actor in tr.find_all("a"):
                    name = voice_actor.text
                    url = voice_actor.get("href")
                    cached_voice_actor = self._cached_voice_actors.get(name)
                    if cached_voice_actor is None:
                        least_works = await self._get_voice_actor_least_works(url)
                        new_voice_actor = VoiceActor(name, least_works)
                        self._cached_voice_actors[name] = new_voice_actor
                        voice_actors.append(new_voice_actor)
                    else:
                        _logger.info(f"Use cached voice actor data for '{name}'")
                        voice_actors.append(cached_voice_actor)

        return voice_actors

    @staticmethod
    async def _get_voice_actor_least_works(voice_actor_url: str) -> int:
        req_voice_actor = await Httpx.get(url=voice_actor_url)
        soup = BeautifulSoup(req_voice_actor.text, "html.parser")
        least_works = len(soup.find_all(class_="work_img_main"))
        return least_works

    @staticmethod
    def get_trial_url(product_page_soup: BeautifulSoup) -> None | str:
        trial_elm = product_page_soup.find(class_="btn_trial")
        if trial_elm is None:
            return None
        raw_trial_url = trial_elm.get("href")
        trial_url = "https:" + raw_trial_url.split("?")[0]
        return trial_url

    async def get_chobit_urls(self) -> None | list[str]:
        req_data = await Httpx.get(
            url="https://chobit.cc/api/v1/dlsite/embed", params={"workno": self._id}
        )

        data = json.loads(req_data.text[9:-1])

        works = data["works"]
        if not works:
            return None

        work = works[0]

        req_embed = await Httpx.get(url=work["embed_url"])
        soup = BeautifulSoup(req_embed.text, "html.parser")

        urls = []
        if work["file_type"] == "audio":
            track_div = soup.find(class_="track-list")
            for track_elm in track_div.find_all("li"):
                urls.append(track_elm.get("data-src"))
        else:
            video_div = soup.find(class_="video-js vjs-default-skin autoplay")
            for video in video_div.find_all("source"):
                urls.append(video.get("src"))

        return urls
