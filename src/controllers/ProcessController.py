from .BaseController import BaseController
import os 
from models import ProcessingEnums
from controllers import ProjectController
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content : str
    metadata : dict

class ProcessController(BaseController):
    
    def __init__(self,project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
    
    def get_file_extension(self,file_id: str):
        file_extension = os.path.splitext(file_id)[-1]
        return file_extension
    
    def get_file_content(self, file_id:str):

        file_path = os.path.join(self.project_path,file_id)
        if os.path.exists(file_path) == False:
            return None


        file_extension = self.get_file_extension(file_id=file_id)

        
        if file_extension == ProcessingEnums.TXT.value:
            loader =  TextLoader(file_path,encoding = 'utf-8')
            return loader.load()

        if file_extension == ProcessingEnums.PDF.value:
            loader = PyMuPDFLoader(file_path)
            return loader.load()
        return None
    

    def process_file_content(self, file_id:str,file_content: list, chunk_size: int =50, overlap_size: int=10):
        

        if file_content is None:
            return None

        
        
        content_list = [doc.page_content for doc in file_content]
        metadata_list = [doc.metadata for doc in file_content]

        # text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_size,length_function=len)
        # chunks = text_splitter.create_documents(content_list,metadatas=metadata_list)

        chunks = self.simple_text_splitter(
            text=content_list,
            metadata=metadata_list,
            chunk_size=chunk_size
        )

        return chunks
    


    def simple_text_splitter(self,text: List[str] , metadata: List[dict], chunk_size:int , splitter_tag: str = '\n' ):
        full_text = ",".join(text)
        lines = [doc .strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1]
        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata= {}
                ))
                current_chunk = ""
        
        if len(current_chunk) > 0:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata= {}
                ))
        return chunks