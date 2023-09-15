import weaviate
from sqlalchemy import create_engine, select
from .model import Base, IconChecksum
from sqlalchemy.orm import Session
import typing


class ApplicationRepository:
    def __init__(self, weaviate_endpoint: "str", mysql_dsn: "str") -> None:
        self.sql_engine = create_engine(mysql_dsn, echo=False)
        self.weaviate_client = weaviate.Client(weaviate_endpoint)
        self.weaviate_client.schema.get()

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
