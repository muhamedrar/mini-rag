from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.dbEnums import DbEnums
from bson.objectid import ObjectId 
from pymongo import InsertOne
class ChunkModel(BaseDataModel):

    def __init__(self, db_client:object):
        super().__init__(db_client= db_client)
        self.db_client = db_client


    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        return instance


    async def create_chunk(self, chunk_data: DataChunk):
        result = await self.collection.insert_one(chunk_data.model_dump(by_alias=True, exclude_unset=True))
        chunk_data._id = result.inserted_id
        
        return chunk_data

    async def get_chunk(self,chunk_id:str):
        result = await self.collection.find_one({
            "_id":ObjectId(chunk_id)
        }
        )
        if result is None:
            return None
        
        return DataChunk(**result)
    

    async def get_project_chunks(self, project_id:ObjectId, page: int = 1, page_size: int = 20):
        skip = (page - 1) * page_size
        records = self.collection.find({
            "chunk_project_id": project_id
        }).skip(skip).limit(page_size)
        

        results = []

        async for record in records:
            results.append(DataChunk(**record))

        return results
        

    async def insert_many_chunks(self,chunks: list,batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations =[
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            await self.collection.bulk_write(operations)
        return len(chunks)
    

    async def delete_chunks_by_projec_id(self, projec_id:ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": projec_id
        })
        return result.deleted_count