import json

from .icon_data import IconData

from dataclasses import dataclass


@dataclass
class IconEmbeddings:
    icon_data: IconData
    embeddings: list


class CollectionInformation:
    embedder: str
    index: str
    full_name: str

    def __init__(self, embedder_name: str, index: str) -> None:
        self.embedder = embedder_name
        self.index = index
        self.full_name = self.generate_full_name(
            embedder_name,
            index,
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "embedder": self.embedder,
                "index": self.index,
                "full_name": CollectionInformation.generate_full_name(
                    self.embedder,
                    self.index,
                ),
            }
        )

    @staticmethod
    def generate_full_name(embedder: str, index: str):
        return f"{embedder}_{index}"

    @staticmethod
    def from_json(v: str):
        data = json.loads(v)
        return CollectionInformation(
            embedder_name=data["embedder"],
            index=data["index"],
        )
