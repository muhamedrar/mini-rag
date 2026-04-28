from .BaseController import BaseController
from models.db_schemas.minirag.schemas import Project, DataChunk
from stores.llms.LLMEnums import DocumentTypeEnums
from typing import List
import json
from fastapi.responses import JSONResponse
from models.enums.ResponseEnums import ResponseSignal

class NlpController(BaseController):
    def __init__(self, vector_db_client, llm_client, embed_client,template_parser = None):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.llm_client = llm_client
        self.embed_client = embed_client
        self.template_parser = template_parser

    def create_collection_name(self,project_id: str):
        collection_name = f"project_{self.vector_db_client.default_vector_dim}_{project_id}"
        return collection_name.strip()
    
    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.id)
        return await self.vector_db_client.delete_collection(collection_name=collection_name)
    
    async def get_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.id)
        info = await self.vector_db_client.get_collection_info(collection_name=collection_name)
        return info
    

    async def index_into_vector_db(self, project: Project, chunk_ids:List[int] , data_chunks: list[DataChunk], do_reset: bool = False):
        collection_name = self.create_collection_name(project_id=project.id)

        texts = [chunk.chunk_text for chunk in data_chunks]
        metadatas = [chunk.chunk_metadata for chunk in data_chunks]
        vectors = self.embed_client.embed_text(text=texts, document_type=DocumentTypeEnums.DOCUMENT.value)

        _ = await self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_dimension=self.embed_client.embedding_model_size,
            do_reset=do_reset
        )


        _ = await self.vector_db_client.insert_many(
            record_ids=chunk_ids,
            collection_name=collection_name,
            text=texts,
            vector=vectors,
            metadata=metadatas
        )

        return True
    
    async def search_in_vector_db(self, project: Project, query: str, limit: int = 5):
        collection_name = self.create_collection_name(project_id=project.id)

        query_vector = self.embed_client.embed_text(text=query, document_type=DocumentTypeEnums.QUERY.value)

        if query_vector is None:
           return False
        
        if isinstance(query_vector, list) or len(query_vector) == 0:
            query_vector = query_vector[0]

        search_results = await self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        if search_results is None:
            return False

        return search_results

    
    async def answer_rag_qestion(self, project:Project, query:str, limit: int = 10):

        retrived_docs = await self.search_in_vector_db(
            project=project,
            query=query,
            limit=limit
        )

        # construct llm prompt

        system_prompt =  self.template_parser.get("rag","system_prompt")

        docs_prompt = [
            self.template_parser.get("rag","documents_prompt",{
                "doc_no" : idx+1,
                "chunk_text":self.llm_client.process_text(doc.text)
            })
            for idx, doc in enumerate(retrived_docs)
        ]
        docs_text = "\n\n".join(docs_prompt)

        footer_prompt =  self.template_parser.get("rag","footer_prompt",{
            "query":query
        })

        chat_history = [
           self.llm_client.construct_prompt(
               prompt = system_prompt,
               role = self.llm_client.enums.ROLE_SYSTEM.value
           )
        ]

        full_prompt = f"{docs_text}\n\n{footer_prompt}"

        answer = self.llm_client.generate_text(
            prompt = full_prompt,
            chat_history = chat_history,
            
            
        )


        return answer, full_prompt, chat_history