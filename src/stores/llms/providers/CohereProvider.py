import cohere 
from ..LLMinterface import LLMInterface
import logging
from ..LLMEnums import CohereEnums, DocumentTypeEnums


class CohereProvider(LLMInterface):
    def __init__(self,api_key: str,
                 default_input_max_characters: int = 1000,
                 default_output_max_tokens: int = 1000,
                 default_temperature: float = 0.1):
        
        self.api_key = api_key
        

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature


        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_model_size = None
        
        self.enums = CohereEnums

        self.client = cohere.Client(api_key= self.api_key)

        self.logger = logging.getLogger(__name__)



    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_model_size = embedding_size

    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float = None) :

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        if not self.client:
            self.logger.error("Cohere client is not set")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model for Cohere is not set")
            return None
        
        response = self.client.chat(
            message=prompt,
            model=self.generation_model_id,
            temperature=temperature ,
            max_tokens=max_output_tokens ,
            chat_history=chat_history
            )
        if not response or not response.text:
            self.logger.error("No response returned from Cohere")
            return None
        
        return response.text
    

    def embed_text(self, text: str,document_type: str = None) :
        if not self.client:
            self.logger.error("Cohere client is not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere is not set")
            return None
        
        input_type = CohereEnums.DOCUMENT.value 
        if document_type == DocumentTypeEnums.QUERY.value:
            input_type = CohereEnums.QUERY.value

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[text],
            input_type=input_type,
            embedding_types=['float']
            )
        if not response or not response.embeddings or not response.embeddings.float_:
            self.logger.error("No embedding returned from Cohere")
            return None
        
        return response.embeddings.float_[0]

        
    

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
    

    def process_text(self,text:str):
        return text[:self.default_input_max_characters].strip()