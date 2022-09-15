from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, Enum, TIMESTAMP, inspect
import enum

from utils.db import Base


class SystemItemType(str, enum.Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class SystemItem(Base):
    __tablename__ = "system_item"
    __table_args__ = {'schema': 'files'}

    id = Column(String(256), primary_key=True)
    parent_id = Column(String(256), ForeignKey('files.system_item.id', ondelete="CASCADE"), nullable=True)
    size = Column(Integer, nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    itemtype = Column(Enum(SystemItemType))
    url = Column(String(256), nullable=True)

    def _asdict(self) -> dict:
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class SystemItemHistory(Base):
    __tablename__ = "system_item_history"
    __table_args__ = {'schema': 'files'}

    id = Column(Integer, primary_key=True)
    item_id = Column(String(256), ForeignKey('files.system_item.id', ondelete="CASCADE"), nullable=False)
    parent_id = Column(String(256), ForeignKey('files.system_item.id', ondelete="CASCADE"), nullable=True)
    size = Column(Integer, nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    itemtype = Column(Enum(SystemItemType))
    url = Column(String(256), nullable=True)

    def _asdict(self) -> dict:
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
