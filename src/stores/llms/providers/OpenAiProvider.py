from openai import OpenAI
from ..LLMinterface import LLMInterface
import logging
from ..LLMEnums import OpenAiEnums

class OpenAiProvider(LLMInterface):
    def __init__(self,api_key: str,
                 api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_output_max_tokens: int = 1000,
                 default_temperature: float = 0.1):
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature


        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_model_size = None

        self.enums = OpenAiEnums


        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_model_size = embedding_size


    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float = None) :
        
        if not self.client:
            self.logger.error("OpenAI client is not set")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI  is not set")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history.append(self.construct_prompt(prompt, OpenAiEnums.ROLE_USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("No response returned from OpenAI")
            return None
        

        return response.choices[0].message.content


    def embed_text(self, text: str,document_type: str = None) :
        
        if not self.client:
            self.logger.error("OpenAI client is not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set")
            return None
        
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id
        )

        if not response or not response.data or len(response.data) == 0:
            self.logger.error("No embedding returned from OpenAI")
            return None
        
        return response.data[0].embedding
    

    def construct_prompt(self, prompt: str, role: str) :
        return {
            "role": role,
            "content":prompt
        }
    
    ## helper method
    def process_text(self,text:str):
        return text[:self.default_input_max_characters].strip()