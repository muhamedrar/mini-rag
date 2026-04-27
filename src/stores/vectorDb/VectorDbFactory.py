from .providers import QdrantDb , PGVectorDb
from .VectorDbEnums import VectorDbEnums
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker

class VectorDbFactory:
    def __init__(self, config:dict, db_client: sessionmaker = None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client
    def create_provider(self, provider_name: str):

        
        
        if provider_name == VectorDbEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)
            return QdrantDb(
                db_client=db_path,
                distance_method=self.config.VECTOR_DISTANCE_METHOD
            )
        

        if provider_name == VectorDbEnums.PGVECTOR.value:
            
            return PGVectorDb(
                db_client=self.db_client,
                default_vector_dim = self.config.EMBEDDING_MODEL_SIZE,
                distance_method=self.config.VECTOR_DISTANCE_METHOD,
                index_vector_threshold=self.config.VECTOR_DB_PGVECTOR_INDEX_THREADHOLD,

            )
        raise ValueError(f"Unsupported provider: {provider_name}")