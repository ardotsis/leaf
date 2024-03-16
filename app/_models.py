from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceActor:
    name: str
    least_work: int


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    url: str
    voice_actors: list[VoiceActor]
    trial_file_url: None | str
    chobit_urls: None | list[str]
