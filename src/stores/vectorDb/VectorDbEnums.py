from enum import Enum

class VectorDbEnums(Enum):
    QDRANT = "Qdrant"
    PGVECTOR = "Pgvector"


class DistanceMethod(Enum):
    COSINE = "cosine"
    DOT_PRODUCT = "dot"


class pgvectorTableSchema(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "Pgvector"

class pgvectorDistanceMethod(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class pgvectorIndexType(Enum):
    IVFFLAT = "IVFFLAT"
    HNSW = "HNSW"