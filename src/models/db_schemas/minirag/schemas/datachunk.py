from minirag.schemas.minirag_base import sqlalchemyBase
from sqlalchemy import Column, Integer,ForeignKey, DateTime,func ,String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid
from pydantic import BaseModel

class DataChunk(sqlalchemyBase):

    __tablename__ = "chunks"

    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid = Column(UUID, default=uuid.uuid4, unique=True, nullable=False)

    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_metadata = Column(Integer, nullable=False)

    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    chunk_assit_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False )
    upated_at = Column(DateTime(timezone=True),onupdate=func.now(), nullable=True)

    project = relationship("Project", backref="chunks")
    asset = relationship("Asset", backref="chunks")


    __table_args__ = {
        Index('ix_chunk_project_id', chunk_project_id),
        Index('ix_chunk_assit_id', chunk_assit_id),
    }


class RetrievedDocument(BaseModel):
    score: float
    text: str