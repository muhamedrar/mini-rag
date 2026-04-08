from enum import Enum

class LLMType(Enum):
    OPENAI = "OpenAI"
    COHERE = "Cohere"


class OpenAiEnums(Enum):
    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

class CohereEnums(Enum):
    ROLE_SYSTEM = "SYSTEM"
    ROLE_USER = "USER"
    ROLE_ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeEnums(Enum):
    DOCUMENT = "document"
    QUERY = "query"