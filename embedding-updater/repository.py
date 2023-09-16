import pymilvus
import core
import typing
import json

from logger import log
from pymilvus.client.types import LoadState

MILVUS_INDEX_METHOD = typing.Literal["L2", "IP"]
MILVUS_INDEX_METHOD_OPTS = list(typing.get_args(MILVUS_INDEX_METHOD))


class ApplicationRepository:
    checksum_collection_name = "checksums"

    def __init__(
        self,
        milvus_uri: "str",
        milvus_api_key: "str",
        milvus_db: "str",
        embedder: core.Embedder,
        indexing_metric: "MILVUS_INDEX_METHOD" = "L2",
    ) -> None:
        # Connect milvus
        self.milvus_cleint_alias = "default"
        pymilvus.connections.connect(
            alias=self.milvus_cleint_alias,
            uri=milvus_uri,
            token=milvus_api_key,
            db_name=milvus_db,
        )

        # Prepare Milvus collection
        log.info("Checking collection")
        embedding_collection_name = self.get_embedding_collection_name(
            embedder, indexing_metric
        )
        checksum_collection_name = self.get_checksum_collection_name()

        # Check if all collection exist
        embeddings_collection = self.collection_exists(embedding_collection_name)
        checksum_collection = self.collection_exists(checksum_collection_name)
        if embeddings_collection is None:
            log.info(
                f"Embedding Collection not exist, creating collection of {embedding_collection_name} with {indexing_metric} indexing"
            )
            embeddings_collection = self.create_new_embedding_collection(
                embedder,
                indexing_metric,
            )
            log.info("Embedding Collection created")

        if checksum_collection is None:
            log.info(
                f"Checksum Collection not exist, creating collection of {checksum_collection_name}"
            )
            checksum_collection = self.craete_new_checksum_collection()
            log.info("Checksum Collection created")

        # Check if all collection loaded
        if not self.collection_is_loaded(embeddings_collection):
            log.info("Embeddings Collection is not loadded, loading the collection")
            self.load_collection(embeddings_collection)
            log.info("Embeddings Collection loaded")
        if not self.collection_is_loaded(checksum_collection):
            log.info("Checksum Collection is not loadded, loading the collection")
            self.load_collection(checksum_collection)
            log.info("Checksum Collection loaded")

        self.checksum_collection = checksum_collection
        self.embedding_collection = embeddings_collection
        log.info("Collection checked")

    def collection_exists(self, collection_name: str) -> pymilvus.Collection | None:
        collection_exist = pymilvus.utility.has_collection(collection_name)
        if not collection_exist:
            return None
        return pymilvus.Collection(
            name=collection_name,
            using=self.milvus_cleint_alias,
        )

    def craete_new_checksum_collection(
        self,
    ) -> pymilvus.Collection:
        """
        Only creates collection.
        Before doing query, you need to load it using `load_collection()` methods
        """
        id = pymilvus.FieldSchema(
            name="id",
            dtype=pymilvus.DataType.VARCHAR,
            is_primary=True,
            max_length=5,
        )

        checksums = pymilvus.FieldSchema(
            name="checksums",
            dtype=pymilvus.DataType.VARCHAR,
            max_length=32,
        )

        dummy_embedding = pymilvus.FieldSchema(
            name="embedding",
            dtype=pymilvus.DataType.FLOAT_VECTOR,
            dim=32,  # Dummy vector
        )

        schema = pymilvus.CollectionSchema(
            fields=[id, checksums, dummy_embedding],
            description=f"An checksums collection of react icons for {self.checksum_collection_name}",
        )

        collection = pymilvus.Collection(
            self.checksum_collection_name,
            schema=schema,
            using=self.milvus_cleint_alias,
        )
        index_params = {
            "metric_type": "L2",
            "index_type": "FLAT",
        }
        collection.create_index(
            field_name=dummy_embedding.name,
            index_params=index_params,
        )
        return collection

    def create_new_embedding_collection(
        self,
        embedder: core.Embedder,
        indexing_metric: "MILVUS_INDEX_METHOD" = "L2",
    ) -> pymilvus.Collection:
        """
        Only creates collection.
        Before doing query, you need to load it using `load_collection()` methods
        """
        collection_name = self.get_embedding_collection_name(
            embedder,
            indexing_metric,
        )
        id = pymilvus.FieldSchema(
            name="id",
            dtype=pymilvus.DataType.VARCHAR,
            is_primary=True,
            max_length=256,
        )
        parent_name = pymilvus.FieldSchema(
            name="parent_name",
            dtype=pymilvus.DataType.VARCHAR,
            max_length=5,
        )
        icon_name = pymilvus.FieldSchema(
            name="icon_name",
            dtype=pymilvus.DataType.VARCHAR,
            max_length=256,
        )
        embedding = pymilvus.FieldSchema(
            name="embedding",
            dtype=pymilvus.DataType.FLOAT_VECTOR,
            dim=embedder.num_dimensions(),
        )
        schema = pymilvus.CollectionSchema(
            fields=[id, parent_name, icon_name, embedding],
            description=json.dumps(
                {
                    "embedder": embedder.name(),
                    "index": indexing_metric,
                }
            ),
        )
        collection = pymilvus.Collection(
            collection_name,
            schema=schema,
            using=self.milvus_cleint_alias,
        )
        index_params = {
            "metric_type": indexing_metric,
            "index_type": "FLAT",
        }
        collection.create_index(
            field_name=embedding.name,
            index_params=index_params,
        )
        return collection

    def collection_is_loaded(self, collection: pymilvus.Collection):
        collection = pymilvus.Collection(
            collection.name, using=self.milvus_cleint_alias
        )
        load_state: LoadState = pymilvus.utility.load_state(collection.name)
        return load_state == LoadState.Loaded

    def load_collection(self, collection: pymilvus.Collection):
        collection = pymilvus.Collection(
            collection.name, using=self.milvus_cleint_alias
        )
        collection.load()
        pymilvus.utility.wait_for_loading_complete(collection.name)

    def get_icon_entity_id(self, icon: core.IconData) -> "str":
        return f"{icon.parent_name}_{icon.icon_name}"

    def get_embedding_collection_name(
        self, collection_name: core.Embedder, indexing: str
    ) -> str:
        return f"{collection_name.name()}_{indexing}"

    def get_checksum_collection_name(self) -> "str":
        return self.checksum_collection_name

    def get_checksum_parent_icon(self, parent_id: "str") -> "str | None":
        search_query = f"id in ['{parent_id}']"
        log.debug(f"Repository: search query {search_query}")

        # Search for entities
        res = self.checksum_collection.query(
            expr=search_query,
            output_fields=[
                "checksums",
            ],
        )

        log.debug(
            f"Repository: Get Checksum query: {search_query} | Get Checksum resulst: {res}"
        )

        if len(res) == 0:
            return None

        return res[0]["checksums"]

    def add_or_update_icon_checksum(self, parent_id: "str", checksum: "str"):
        search_query = f"id in ['{parent_id}']"
        log.debug(f"Repository: search query {search_query}")
        # Search for entities
        res = self.checksum_collection.query(
            expr=search_query,
            output_fields=[
                "id",
            ],
        )
        log.debug(
            f"Repository: Get Checksum query: {search_query} | Get Checksum resulst: {res}"
        )
        if len(res) != 0:
            # Delete available data
            self.checksum_collection.delete(search_query)

        # Add Entity
        entities = [[parent_id], [checksum], [[0 for _ in range(32)]]]  # Dummy vector
        self.checksum_collection.insert(entities)
        self.checksum_collection.flush()

    # TODO: Refactor this code so that we can do batched embeded_icon inputs
    def add_or_update_icon(
        self,
        embeded_icon: typing.List[core.IconEmbeddings],
    ):
        ids = [self.get_icon_entity_id(icon.icon_data) for icon in embeded_icon]
        search_query = "id in [" + ",".join([f"'{id}'" for id in ids]) + "]"
        log.debug(f"Repository: search query {search_query}")

        # Search for entities
        res = self.embedding_collection.query(
            expr=search_query,
            output_fields=[
                "id",
            ],
        )
        if len(res) != 0:
            # Delete available data
            self.embedding_collection.delete(search_query)

        # Add Entity
        parent_names = [icon.icon_data.parent_name for icon in embeded_icon]
        icon_name = [icon.icon_data.icon_name for icon in embeded_icon]
        embeddings = [icon.embeddings for icon in embeded_icon]
        entities = [
            ids,
            parent_names,
            icon_name,
            embeddings,
        ]
        self.embedding_collection.insert(entities)
        self.embedding_collection.flush()
