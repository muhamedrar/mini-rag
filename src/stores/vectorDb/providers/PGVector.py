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
            distance_method: str = None
    ):
        self.db_client = db_client
        self.default_vector_dim = default_vector_dim
        self.distance_method = distance_method

        self.pgvector_table_prefix = pgvectorTableSchema._PREFIX.value

        self.logger = logging.getLogger('uvicorn')


    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector;"
                ))
            await session.commit()

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
                await session.commit()
        return True
    
    async def create_collection(self, collection_name: str, embedding_dimension: int, do_reset: bool = False):
        if do_reset == 1:
            _ = await self.delete_collection(collection_name=collection_name)
        
        is_collection_exist = await self.is_collection_exist(collection_name=collection_name)

        if not is_collection_exist:
            self.logger.info(f"Creating collection :{collection_name}")

            async with self.db_client as session:
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
                    await session.commit()
            return True
        else:
            self.logger.info(f"Collection {collection_name} already exists.")
            return False