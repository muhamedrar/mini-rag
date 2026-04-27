from ..VectorDbEnums import (
    pgvectorIndexType,
    pgvectorDistanceMethod,
    pgvectorTableSchema,
    DistanceMethod

)

from ..VectorDbInterface import VectorDbInterface
import logging
from typing import List
from models.db_schemas import RetrievedDocument
from sqlalchemy.sql import text as sql_text
import json 

class PGVectorDb(VectorDbInterface):
    def __init__(
            self,
            db_client,
            default_vector_dim: int = 786,
            index_vector_threshold: int = 100,
            distance_method: str = None
    ):
        self.db_client = db_client
        self.default_vector_dim = default_vector_dim
        self.distance_method = distance_method
        self.index_vector_threshold = index_vector_threshold

        self.pgvector_table_prefix = pgvectorTableSchema._PREFIX.value

        self.logger = logging.getLogger('uvicorn')

        self.default_index_name = lambda collection_name : f"{collection_name}_vector_idx"
        


    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector;"
                ))

    async def disconnect(self):
        pass

    async def is_collection_exist(self, collection_name: str) -> bool:
        async with self.db_client() as session:
            result = await session.execute(
                sql_text("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_tables 
                        WHERE tablename = :collection_name
                    )
                """),
                {"collection_name": collection_name}
            )
            return result.scalar()

    async def list_all_collections(self) -> List:
        async with self.db_client() as session:
            result = await session.execute(
                sql_text("""
                    SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix
                """),
                {'prefix':self.pgvector_table_prefix})
            return result.scalars().all()
    
    async def get_collection_info(self, collection_name: str) -> dict:

        async with self.db_client() as session:
                    table_info = await session.execute(
                        sql_text("""
                            SELECT schemansessioname, tablename , tableowner, hasindexes
                            FROM pg_tables 
                            WHERE tablename = :collection_name
                        """),
                        {'collection_name':collection_name}
                        )
                    
                    count = await session.execute(
                        sql_text(f"""
                            SELECT COUNT(*) FROM :collection_name
                        """),
                        {'collection_name':collection_name}
                    )
                    
                    table_data = table_info.fetchone()
                    count = count.scalar()

                    if not table_info:
                        return None
                    return {
                        "table_info": dict(table_data),
                        "table_count": count
                    }
        


    async def delete_collection(self, collection_name: str):
        async with self.db_client as session:
             async with session.begin():
                self.logger.info(f"Deleting collection : {collection_name}")
                await session.execute(
                        sql_text("""
                            DROP table if EXISTS :collection_name
                        """),
                        {'collection_name':collection_name}
                        )
        return True
    
    async def create_collection(self, collection_name: str, embedding_dimension: int, do_reset: bool = False):
        if do_reset == 1:
            _ = await self.delete_collection(collection_name=collection_name)
        
        is_collection_exist = await self.is_collection_exist(collection_name=collection_name)

        if not is_collection_exist:
            self.logger.info(f"Creating collection :{collection_name}")

            async with self.db_client() as session:
                async with session.begin():
                    create_table = sql_text(f"""
                                            CREATE TABLE {collection_name} (
                                                {pgvectorTableSchema.ID.value} bigserial PRIMARY KEY,
                                                {pgvectorTableSchema.TEXT.value} text,
                                                {pgvectorTableSchema.VECTOR.value} vector({embedding_dimension}),
                                                {pgvectorTableSchema.CHUNK_ID.value} integer,
                                                {pgvectorTableSchema.METADATA.value} jsonb DEFAULT '{{}}',
                                                FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
                                            )
                                            """)
                    await session.execute(create_table)
            return True
        else:
            self.logger.info(f"Collection {collection_name} already exists.")
            return False
        

    async def is_index_exist(self, collection_name:str) ->bool:
        index_name = self.default_index_name(collection_name=collection_name)
        async with self.db_client() as session:
            query = sql_text(f"""
                                SELECT EXISTS (
                                    SELECT 1 FROM pg_indexes
                                    WHERE tablename = :collection_name
                                    AND indexname = :index_name
                                )
                             """)
            result = await session.execute(query,
                                  {
                                      "collection_name": collection_name,
                                       "index_name": index_name
                                  })
            return result.scalar()


    async def create_index(self, collection_name:str, index_type: str = pgvectorIndexType.HNSW.value):
         
        is_index_exist = await self.is_index_exist(collection_name=collection_name)
        if is_index_exist:
            self.logger.info(f"Index already exists for collection : {collection_name}")
            return True

        async with self.db_client() as session:
            async with session.begin():  
                count_sql = sql_text(f"""
                    SELECT COUNT(*) FROM :collection_name
                """)
                result = await session.execute(count_sql, {"collection_name": collection_name})
                rescord_count = result.scalar_one()

                if rescord_count < self.index_vector_threshold:
                    self.logger.info(f"Record count {rescord_count} is less than index creation threshold {self.index_vector_threshold}. Skipping index creation for collection : {collection_name}")
                    return False
                self.logger.info(f"Creating index for collection : {collection_name} with index type : {index_type}")
                create_index_sql = sql_text(f"""
                    CREATE INDEX {self.default_index_name(collection_name=collection_name)}
                    ON {collection_name}
                    USING {index_type} ({pgvectorTableSchema.VECTOR.value} {self.distance_method})
                """)
                await session.execute(create_index_sql)
                self.logger.info(f"Index created successfully for collection : {collection_name}")
                return True
            

    async def reset_index(self, collection_name:str):
        async with self.db_client() as session:
            async with session.begin():
                drop_index_sql = sql_text(f"""
                    DROP INDEX IF EXISTS {self.default_index_name(collection_name=collection_name)}
                """)
                await session.execute(drop_index_sql)
                self.logger.info(f"Index dropped successfully for collection : {collection_name}")
                
        return await self.create_index(collection_name=collection_name)

            


    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict=None, record_id: str=None):
        is_exist = await self.is_collection_exist(collection_name=collection_name)
        if not is_exist:
            self.logger.error(f"Can not insert record in non exsiting table : {collection_name}")
            return False
        
        if record_id == None:
            self.logger.error(f"Can not insert record with none CHUNK_ID : {collection_name}")
            return False

        
        async with self.db_client() as session:
                async with session.begin():
                    insert_record = sql_text(f"""
                                             INSERT INTO {collection_name} 
                                            ({pgvectorTableSchema.TEXT.value},{pgvectorTableSchema.VECTOR.value},{pgvectorTableSchema.CHUNK_ID.value},{pgvectorTableSchema.METADATA.value})
                                            VALUES (:text, :vector, :chunk_id, :metadata)
                                             """)

                    await session.execute(insert_record, {
                        "text": text,
                        "vector": '[' + ",".join([str(v) for v in vector]) + ']',
                        "chunk_id": record_id,
                        "metadata": metadata or {}
                    })
        self.logger.info(f"Record inserted successfully into  : {collection_name}")
        return True
    
    async def insert_many(self, collection_name: str, text: list, vector: list, record_ids: list,  metadata: list=None, batch_size: int=50):

        is_exist = await self.is_collection_exist(collection_name=collection_name)
        if not is_exist:
            self.logger.error(f"Can not insert records in non exsiting table : {collection_name}")
            return False
        
        if len(record_ids) != len(vector) :
            self.logger.error(f"Length of record_ids and vector must be same : {collection_name}")
            return False
        if not metadata or len(metadata) == 0:
            metadata = [None] * len(text)


        async with self.db_client() as session:
                async with session.begin():
                    insert_record = sql_text(f"""
                                             INSERT INTO {collection_name} 
                                            ({pgvectorTableSchema.TEXT.value},{pgvectorTableSchema.VECTOR.value},{pgvectorTableSchema.CHUNK_ID.value},{pgvectorTableSchema.METADATA.value})
                                            VALUES (:text, :vector, :chunk_id, :metadata)
                                             """)
                    for i in range(0, len(text), batch_size):
                        batch_text = text[i:i+batch_size]
                        batch_vector = vector[i:i+batch_size]
                        batch_record_ids = record_ids[i:i+batch_size]
                        batch_metadata = metadata[i:i+batch_size]

                        await session.execute(insert_record, [
                            {
                                "text": t,
                                "vector": '[' + ",".join([str(v) for v in vec]) + ']',
                                "chunk_id": rid,
                                "metadata": md or {}
                            }
                            for t, vec, rid, md in zip(batch_text, batch_vector, batch_record_ids, batch_metadata)
                        ])
        self.logger.info(f"records inserted successfully into  : {collection_name}")
        return True


    async def search_by_vector(self, collection_name: str, vector: list, limit: int=5)-> List[RetrievedDocument]:
        is_exist = await self.is_collection_exist(collection_name=collection_name)
        if not is_exist:
            self.logger.error(f"Can not search records in non exsiting table : {collection_name}")
            return []
        
        async with self.db_client() as session:
                seach_query = sql_text(f"""
                    SELECT 
                        {pgvectorTableSchema.TEXT.value} as text,
                        1 - {pgvectorTableSchema.VECTOR.value} <-> :vector as score,
                    FROM {collection_name}
                    ORDER BY distance
                    LIMIT :limit
                """)


                result = await session.execute(
                     seach_query,
                     {
                        "vector": '[' + ",".join([str(v) for v in vector]) + ']',
                        "limit": limit
                     }
                )
                records = result.fetchall()

                return[
                    RetrievedDocument(
                        text=record.text,
                        score=record.score
                     )
                    for record in records
                ]
        

