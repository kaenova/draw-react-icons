from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class IconChecksum(Base):
    __tablename__ = "icon_checksum"
    parent_id: Mapped[str] = mapped_column(String(5), primary_key=True)
    checksum: Mapped[str] = mapped_column(String(32))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
