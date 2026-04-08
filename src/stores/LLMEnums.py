from enum import Enum

class LLMType(Enum):
    OPENAI = "OpenAI"
    COHERE = "Cohere"


class OpenAiEnums(Enum):
    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"