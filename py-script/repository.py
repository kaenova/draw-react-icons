import typing
import core
import uuid

import qdrant_client.conversions.common_types as qcT

from core import log
from qdrant_client import QdrantClient
from qdrant_client.http import models

QDRANT_INDEX_METHOD = {
    "cosine": models.Distance.COSINE,
    "dot": models.Distance.DOT,
    "euclid": models.Distance.EUCLID,
}

QDRANT_INDEX_METHOD_OPTS = QDRANT_INDEX_METHOD.keys()


class ApplicationRepository:
    checksum_collection_name = "checksums"
    checksum_vector_dummy_length = 2

    def __init__(
        self,
        qdrant_uri: str,
        qdrant_api_key: str,
    ) -> None:
        # Connect milvus
        self.qdrant_client = QdrantClient(
            url=qdrant_uri, api_key=qdrant_api_key, prefer_grpc=True, timeout=180
        )

    def collection_exists(self, collection_name: str) -> qcT.CollectionInfo | None:
        try:
            collection = self.qdrant_client.get_collection(collection_name)
            return collection
        except:
            return None

    def craete_new_checksum_collection(
        self,
    ) -> qcT.CollectionInfo:
        """
        Only creates collection.
        Before doing query, you need to load it using `load_collection()` methods
        """
        collection = None
        counter = 0
        counter_limit = 10
        while (collection is None) and (counter < counter_limit):
            self.qdrant_client.recreate_collection(
                collection_name=self.checksum_collection_name,
                vectors_config=models.VectorParams(
                    size=self.checksum_vector_dummy_length,
                    distance=models.Distance.DOT,
                ),
                on_disk_payload=True,
            )
            collection = self.collection_exists(self.checksum_collection_name)
            counter += 1
        if collection is None:
            raise RuntimeError("Collection not created")
        return collection

    def create_new_embedding_collection(
        self,
        embedder: core.Embedder,
        indexing_metric: models.Distance,
    ) -> qcT.CollectionInfo:
        """
        Only creates collection.
        Before doing query, you need to load it using `load_collection()` methods
        """
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(),
            index=indexing_metric,
        )
        collection = None
        counter = 0
        counter_limit = 10
        while (collection is None) and (counter < counter_limit):
            self.qdrant_client.recreate_collection(
                collection_name=collection_info.full_name,
                vectors_config=models.VectorParams(
                    size=embedder.num_dimensions(),
                    distance=indexing_metric,
                    on_disk=True,
                ),
                on_disk_payload=True,
                shard_number=3,
            )
            collection = self.collection_exists(collection_info.full_name)
            counter += 1

        if collection is None:
            raise RuntimeError("Collection not created")
        return collection

    def get_icon_entity_id(self, icon: core.IconData) -> "str":
        return f"{icon.parent_name}_{icon.icon_name}"

    def get_embedding_collection_name(
        self, embedder: core.Embedder, indexing: str
    ) -> str:
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(), index=indexing
        )
        return collection_info.full_name

    def get_checksum_collection_name(self) -> "str":
        return self.checksum_collection_name

    def get_checksum(
        self, embedder: core.Embedder, indexing: str
    ) -> typing.Dict[str, str] | None:
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(), index=indexing
        )
        res = self.qdrant_client.scroll(
            collection_name=self.checksum_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="collection_name",
                        match=models.MatchValue(value=collection_info.full_name),
                    )
                ]
            ),
        )[0]

        if (len(res) == 0) or (res[0].payload is None):
            return None

        checksum = res[0].payload.get("checksums", None)
        if checksum is None:
            return None

        return checksum

    def add_or_update_checksum(
        self, embedder: core.Embedder, indexing: str, checksums: typing.Dict[str, str]
    ):
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(), index=indexing
        )
        collection_name = collection_info.full_name
        res = self.qdrant_client.scroll(
            collection_name=self.checksum_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="collection_name",
                        match=models.MatchValue(value=collection_name),
                    )
                ]
            ),
        )[0]

        # Generate new id by default, use available id if available
        point_id = str(uuid.uuid4())
        if len(res) != 0:
            point_id = res[0].id

        self.qdrant_client.upsert(
            wait=True,
            collection_name=self.checksum_collection_name,
            points=models.Batch(
                ids=[point_id],
                vectors=[[0 for _ in range(self.checksum_vector_dummy_length)]],
                payloads=[{"collection_name": collection_name, "checksums": checksums}],
            ),
        )

        return checksums

    def add_or_update_icon(
        self,
        embedder: core.Embedder,
        indexing_metric: models.Distance,
        embeded_icon: typing.List[core.IconEmbeddings],
    ):
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(),
            index=indexing_metric,
        )

        res = self.qdrant_client.scroll(
            collection_name=collection_info.full_name,
            scroll_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="icon_name",
                        match=models.MatchValue(value=icon.icon_data.icon_name),
                    )
                    for icon in embeded_icon
                ]
            ),
        )[0]

        # Delete all ids if available
        if len(res) != 0:
            self.qdrant_client.delete(
                collection_name=collection_info.full_name,
                points_selector=models.PointIdsList(
                    points=[x.id for x in res],
                ),
                wait=True,
            )

        point_ids = [str(uuid.uuid4()) for _ in range(len(embeded_icon))]
        self.qdrant_client.upsert(
            wait=True,
            collection_name=collection_info.full_name,
            points=models.Batch(
                ids=[*point_ids],
                vectors=[x.embeddings for x in embeded_icon],
                payloads=[
                    {
                        "parent_id": x.icon_data.parent_name,
                        "icon_name": x.icon_data.icon_name,
                    }
                    for x in embeded_icon
                ],
            ),
        )

    def disable_indexing(
        self, embedder: core.Embedder, indexing_metric: models.Distance
    ):
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(),
            index=indexing_metric,
        )
        self.qdrant_client.update_collection(
            collection_name=collection_info.full_name,
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=0,
            ),
        )

    def collection_is_ready(
        self, embedder: core.Embedder, indexing_metric: models.Distance
    ):
        collection_internal_info = core.CollectionInformation(
            embedder_name=embedder.name(),
            index=indexing_metric,
        )
        collection_info = self.qdrant_client.get_collection(
            collection_name=collection_internal_info.full_name,
        )
        return collection_info.status == models.CollectionStatus.GREEN

    def enable_indexing(
        self,
        embedder: core.Embedder,
        indexing_metric: models.Distance,
        indexing_threshold: int = 20_000,
    ):
        collection_info = core.CollectionInformation(
            embedder_name=embedder.name(),
            index=indexing_metric,
        )
        self.qdrant_client.update_collection(
            collection_name=collection_info.full_name,
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=indexing_threshold,
            ),
        )
