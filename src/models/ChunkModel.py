from .BaseDataModel import BaseDataModel
from .db_schemas.minirag.schemas import DataChunk
from .enums.dbEnums import DbEnums
from bson.objectid import ObjectId 
from pymongo import InsertOne
from sqlalchemy.future import select
from sqlalchemy import func, delete


class ChunkModel(BaseDataModel):

    def __init__(self, db_client:object):
        super().__init__(db_client= db_client)
        self.db_client = db_client


    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        return instance


    async def create_chunk(self, chunk_data: DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(DataChunk)
            await session.commit()
            await session.refresh(DataChunk)
        return DataChunk
        


    async def get_chunk(self,chunk_id:str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunk).where(DataChunk.id == chunk_id)
                chunk = query.scalar_one_or_none()
        return chunk

            
    

    async def get_project_chunks(self, project_id:ObjectId, page: int = 1, page_size: int = 20):

        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page-1)*page_size).limit(page_size)
            records = await session.execute(stmt).scalars().all()

        return records
    

    
    async def insert_many_chunks(self,chunks: list,batch_size: int = 100):
        
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                      batch = chunks[i:i+batch_size]
                      session.add_all(batch)
            session.commit()
        
        return len(chunks)

    async def delete_chunks_by_projec_id(self, projec_id:ObjectId):
        async with self.db_client() as session:
            async with session.begin():
                stmt = delete(DataChunk).where(DataChunk.chunk_project_id == projec_id)
                result = session.execute(stmt)
                await session.commit()
        return result.rowcount