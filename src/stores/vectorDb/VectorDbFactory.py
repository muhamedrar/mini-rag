from .providers import QdrantDb
from .VectorDbEnums import VectorDbEnums
from controllers.BaseController import BaseController


class VectorDbFactory:
    def __init__(self, config:dict):
        self.config = config
        self.base_controller = BaseController()
    def create_provider(self, provider_name: str):

        db_path = self.base_controller.get_vector_db_path(self.config.VECTOR_DB_PATH)
        
        if provider_name == VectorDbEnums.QDRANT.value:
            return QdrantDb(
                db_path=db_path,
                distance_method=self.config.VECTOR_DISTANCE_METHOD
            )
        
        raise ValueError(f"Unsupported provider: {provider_name}")