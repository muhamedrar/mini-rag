from llms.providers import CohereProvider
from llms.providers import OpenAiProvider ,OllamaProvider
from .LLMEnums import LLMType


class LLmFactory:
    def __init__(self, config:dict):
        self.config = config
    
    def create_provider(self, provider_name: str):
        if provider_name == LLMType.OPENAI.value:
            return OpenAiProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_URI,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.DEFAULT_OUTPUT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE

            )
        if provider_name == LLMType.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.DEFAULT_OUTPUT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE
            )
        
        if provider_name == LLMType.OLLAMA.value:
            return OllamaProvider(
                api_key=self.config.OLLAMA_API_KEY,
                api_url=self.config.oLLAMA_API_URL,
                default_input_max_characters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_tokens=self.config.DEFAULT_OUTPUT_MAX_TOKENS,
                default_temperature=self.config.DEFAULT_TEMPERATURE
            )
        raise ValueError(f"Unsupported provider: {provider_name}")

    