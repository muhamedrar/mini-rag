from .providers import QdrantDb
from .VectorDbEnums import VectorDbEnums
from controllers.BaseController import BaseController


class VectorDbFactory:
    def __init__(self, config:dict):
        self.config = config
        self.base_controller = BaseController()
    def create_provider(self, provider_name: str):

        db_client = self.base_controller.get_database_path(self.config.VECTOR_db_client)
        
        if provider_name == VectorDbEnums.QDRANT.value:
            return QdrantDb(
                db_client=db_client,
                distance_method=self.config.VECTOR_DISTANCE_METHOD
            )
        
        raise ValueError(f"Unsupported provider: {provider_name}")