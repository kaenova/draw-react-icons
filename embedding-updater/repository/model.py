from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class IconChecksum(Base):
    __tablename__ = "icon_checksum"
    parent_id: Mapped[str] = mapped_column(String(5), primary_key=True)
    checksum: Mapped[str] = mapped_column(String(32))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.parent_id!r}, checksum={self.checksum!r})"
