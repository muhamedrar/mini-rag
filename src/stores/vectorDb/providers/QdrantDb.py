from ..VectorDbEnums import VectorDbEnums,DistanceMethod
from ..VectorDbInterface import VectorDbInterface
from qdrant_client import QdrantClient, models
import logging
from typing import List
from models.db_schemas import RetrievedDocument
import json

class QdrantDb(VectorDbInterface):

    def __init__(self,db_path:str,distance_method:str):
        self.db_path = db_path
        self.distance_method = None
        self.client = None

        if distance_method == DistanceMethod.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethod.DOT_PRODUCT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info(f"Connected to Qdrant database at {self.db_path}")

    def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from Qdrant database")

    def is_collection_exist(self,collection_name:str)->bool:
        return self.client.collection_exists(collection_name)
    
     
    def list_all_collections(self) -> List:
        return self.client.get_collections()


   
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name)

    
    def delete_collection(self, collection_name: str):
        if self.is_collection_exist(collection_name=collection_name):
            return self.client.delete_collection(collection_name)

    
    def create_collection(self, collection_name: str, embedding_dimension: int, do_reset: bool = False):
        if do_reset:
            _=self.delete_collection(collection_name)
        if not self.is_collection_exist(collection_name):
            _=self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_dimension, distance=self.distance_method)

            )
            return True
        return False
    

    
    def insert_one(self, collection_name: str, text: str, vector: List, metadata: dict=None, record_id: str=None):
        if not self.is_collection_exist(collection_name):
            self.logger.error(f"could not insert record to collection {collection_name} because it does not exist")
            return False
        
        try:
            _= self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ])
        except Exception as e:
            self.logger.error(f"Error inserting record into collection {collection_name}: {e}")
            return False

        return True


    
    def insert_many(self, collection_name: str, text: List, vector: List, record_ids: List,  metadata: List=None, batch_size: int=50):
        
        if metadata is None:
            metadata = [None] * len(text)
        if record_ids is None:
            record_ids = list(range(0,len(text)))
        
        for i in range(0, len(text), batch_size):
            batch_text = text[i:i+batch_size]
            batch_vector = vector[i:i+batch_size]
            batch_metadata = metadata[i:i+batch_size]
            record_ids_batch = record_ids[i:i+batch_size]
            
            batch_records =[
                models.PointStruct(
                    id=record_ids_batch[x],
                    vector=batch_vector[x],
                    payload={
                        "text": batch_text[x],
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_text))
            ]
            
            try:
                _= self.client.upsert(
                            collection_name=collection_name,
                            points=batch_records)
            except Exception as e:
                self.logger.error(f"Error inserting batch starting at index {i}: {e}")
                return False

        return True
           

    
    def search_by_vector(self, collection_name: str, query: list, limit: int=5):
        result =  self.client.query_points(
            collection_name=collection_name,
            query=query,
            limit=limit
        )

       
        if result is None:
            return False
        

        return [
        RetrievedDocument(
            score=hit.score,
            text=hit.payload.get("text", "") if hit.payload else ""
        ).model_dump()          # ← Convert to dict here
        for hit in result.points
    ]
    
        # return self.client.query_points(
        #     collection_name=collection_name,
        #     query=query,
        #     limit=limit
        # )