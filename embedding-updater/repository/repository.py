import weaviate
from sqlalchemy import create_engine, select
from .model import Base, IconChecksum
from sqlalchemy.orm import Session
import pymilvus
import core
from logger import log

import typing

MILVUS_INDEX_METHOD = typing.Literal["L2", "IP"]
MILVUS_INDEX_METHOD_OPTS = list(typing.get_args(MILVUS_INDEX_METHOD))


class ApplicationRepository:
    def __init__(
        self,
        weaviate_endpoint: "str",
        mysql_dsn: "str",
        milvus_uri: "str",
        milvus_api_key: "str",
        milvus_db: "str",
    ) -> None:
        self.sql_engine = create_engine(mysql_dsn, echo=False)
        self.weaviate_client = weaviate.Client(weaviate_endpoint)
        self.weaviate_client.schema.get()

        self.milvus_cleint_alias = "default"
        pymilvus.connections.connect(
            alias=self.milvus_cleint_alias,
            uri=milvus_uri,
            token=milvus_api_key,
            db_name=milvus_db,
        )

        Base.metadata.create_all(self.sql_engine)

    def get_checksum_parent_icon(self, parent_id: "str") -> "str | None":
        with Session(self.sql_engine) as session:
            stmt = select(IconChecksum).where(IconChecksum.parent_id == parent_id)
            obj = session.scalars(stmt).first()
            return None if obj is None else obj.checksum

    def add_or_update_icon_checksum(self, parent_id: "str", checksum: "str"):
        with Session(self.sql_engine) as session:
            stmt = select(IconChecksum).where(IconChecksum.parent_id == parent_id)
            obj = session.scalars(stmt).first()
            if obj is None:
                # Create
                session.add(IconChecksum(parent_id=parent_id, checksum=checksum))
            else:
                # Update
                obj.checksum = checksum
            session.commit()

    def collection_exists(
        self, embedder: core.Embedder, indexing_metrics: "str"
    ) -> "bool":
        return pymilvus.utility.has_collection(
            self.generate_collection_name(
                embedder,
                indexing_metrics,
            )
        )

    def create_new_collection(
        self,
        embedder: core.Embedder,
        indexing_metric: "MILVUS_INDEX_METHOD" = "L2",
    ):
        collection_name = self.generate_collection_name(
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
            description=f"An embedding collection of react icons for {collection_name} with {indexing_metric}",
        )
        log.debug(f"{schema}")
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

    # TODO: Refactor this code so that we can do batched embeded_icon inputs
    def add_or_update_icon(
        self,
        embeded_icon: "core.IconEmbeddings",
        embedder: core.Embedder,
        indexing: MILVUS_INDEX_METHOD,
    ):
        id = self.generate_icon_entity_id(embeded_icon.icon_data)
        collection = pymilvus.Collection(
            self.generate_collection_name(embedder, indexing)
        )
        search_query = f"id in ['{id}']"

        # Search for entities
        res = collection.query(
            expr=search_query,
            output_fields=[
                "id",
            ],
        )

        if len(res) != 0:
            # Delete available data
            collection.delete(search_query)

        # Add Entity
        parent_name = embeded_icon.icon_data.parent_name
        icon_name = embeded_icon.icon_data.icon_name
        embeddings = embeded_icon.embeddings
        entities = [
            [id],
            [parent_name],
            [icon_name],
            [embeddings],
        ]
        collection.insert(entities)
        collection.flush()

    def generate_icon_entity_id(self, icon: core.IconData) -> "str":
        return f"{icon.parent_name}_{icon.icon_name}"

    def generate_collection_name(
        self, collection_name: core.Embedder, indexing: str
    ) -> str:
        return f"{collection_name.name()}_{indexing}"
