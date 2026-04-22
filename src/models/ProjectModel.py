from .BaseDataModel import BaseDataModel
from .db_schemas.minirag.schemas import Project
from .enums.dbEnums import DbEnums
from bson.objectid import ObjectId 
from sqlalchemy.future import select
from sqlalchemy import func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client:object):
        super().__init__(db_client= db_client)
        self.db_client = db_client    
    
    
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)
        return instance



    

    async def create_project(self, project: Project):

        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        return project
    

    async def get_projct_or_create_one(self, project_id: str):
        async with self.db_client() as session:
                    async with session.begin():
                        query = select(Project).where(Project.id == project_id)
                        project = query.scalar_one_or_none()
                        if project is None:
                            project_record = Project(
                                   id= project_id
                                )
                            project = self.create_project(project= project_record)
                            return project
                        else:
                            return project
                              
        
    
    async def get_all_projects(self, page: int = 1 ,page_size: int = 10):

        async with self.db_client() as session:
            async with session.begin():
                total_records = await session.execute(select(
                      func.count(Project.id)
                 )).scalar_one()
                total_pages = total_records// page_size
                if total_records % page_size != 0:
                    total_pages += 1
                query = select(Project).offset((page-1)*page_size).limit(page_size)
                projects = await session.execute(query).scalars().all()
                return projects, total_pages
        
    

