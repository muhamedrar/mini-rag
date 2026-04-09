from enum import Enum

class VectorDbEnums(Enum):
    QDRANT = "QDRANT"


class DistanceMethod(Enum):
    COSINE = "cosine"
    DOT_PRODUCT = "dot"