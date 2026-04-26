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
                            SELECT schemaname, tablename , tableowner, hasindexes
                            FROM pg_tables 
                            WHERE tablename = :collection_name
                        """),
                        {'collection_name':collection_name})
                    
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
    