from .BaseController import BaseController
from models.db_schemas import Project, DataChunk
from stores.llms.LLMEnums import DocumentTypeEnums
from typing import List


class NlpController(BaseController):
    def __init__(self, vector_db_client, llm_client, embed_client):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.llm_client = llm_client
        self.embed_client = embed_client

    def create_collection_name(self,project_id: str):
        collection_name = f"project_{project_id}"
        return collection_name.strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vector_db_client.delete_collection(collection_name=collection_name)
    
    def get_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vector_db_client.get_collection_info(collection_name=collection_name)
    

    def index_into_vector_db(self, project: Project, chunk_ids:List[int] , data_chunks: list[DataChunk], do_reset: bool = False):
        collection_name = self.create_collection_name(project_id=project.project_id)

        texts = [chunk.chunk_text for chunk in data_chunks]
        metadatas = [chunk.chunck_metadata for chunk in data_chunks]
        vectors = [
            self.embed_client.embed_text(text=text, document_type=DocumentTypeEnums.DOCUMENT.value)
            for text in texts
        ]

        _ = self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_dimension=self.embed_client.embedding_model_size,
            do_reset=do_reset
        )


        _ = self.vector_db_client.insert_many(
            record_ids=chunk_ids,
            collection_name=collection_name,
            text=texts,
            vector=vectors,
            metadata=metadatas
        )

        return True

    