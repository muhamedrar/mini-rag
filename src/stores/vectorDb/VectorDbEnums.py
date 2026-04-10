from enum import Enum

class VectorDbEnums(Enum):
    QDRANT = "Qdrant"


class DistanceMethod(Enum):
    COSINE = "cosine"
    DOT_PRODUCT = "dot"