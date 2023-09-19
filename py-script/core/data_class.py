from dataclasses import dataclass
from .icon_data import IconData


@dataclass
class IconEmbeddings:
    icon_data: IconData
    embeddings: list
