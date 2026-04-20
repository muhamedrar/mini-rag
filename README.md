# Mini-RAG

Mini-RAG is a small FastAPI-based retrieval-augmented generation API. It lets you upload project files, split them into chunks, store chunk metadata in MongoDB, index embeddings in a local Qdrant store, and then search or answer questions against the indexed content with an LLM provider.

The codebase currently supports:

- File upload for `.txt` and `.pdf`
- Chunking with LangChain text splitters
- MongoDB for project, asset, and chunk metadata
- Local embedded Qdrant for vector search
- `OpenAI` and `Cohere` provider backends
- OpenAI-compatible endpoints through the `OpenAI` provider, including Ollama
- English and Arabic RAG prompt templates

## How It Works

1. Upload a file to a `project_id`.
2. The app stores the physical file under `src/assets/files/<project_id>/`.
3. The file is processed into chunks and the chunks are stored in MongoDB.
4. The chunks are embedded and indexed into a Qdrant collection named `project_<project_id>`.
5. You can search the vector index or generate a RAG answer from retrieved chunks.

## Stack

- API: FastAPI
- Database: MongoDB
- Vector store: local Qdrant via `qdrant-client`
- File parsing: LangChain loaders + PyMuPDF
- LLM providers: OpenAI-compatible APIs and Cohere

## Project Layout

```text
mini-rag/
├── README.md
├── docker/
│   └── docker-compose.yml
└── src/
    ├── main.py
    ├── requirements.txt
    ├── .env
    ├── controllers/
    ├── helpers/
    ├── models/
    ├── routes/
    └── stores/
        ├── llms/
        └── vectorDb/
```

## Prerequisites

- Python 3.10+ recommended
- `pip`
- Docker and Docker Compose for MongoDB and optional Ollama
- Conda is optional, not required

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd mini-rag
```

### 2. Create and activate a virtual environment

With Conda:

```bash
conda create -n mini-rag python=3.10
conda activate mini-rag
```

With `venv`:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

The requirements file lives under `src/`.

```bash
pip install -r src/requirements.txt
```

### 4. Start MongoDB

The repository ships with a Docker Compose file for MongoDB only.

Set the required MongoDB credentials in your shell or compose env file:

```bash
export MONGO_INITDB_ROOT_USERNAME=admin
export MONGO_INITDB_ROOT_PASSWORD=admin
```

Then start MongoDB:

```bash
docker compose -f docker/docker-compose.yml up -d
```

The compose file maps MongoDB to `localhost:27007`.

### 5. Configure `src/.env`

Run the API from inside `src/` so the app can load `.env` correctly. The settings loader uses `env_file = ".env"`, which is resolved relative to the current working directory.

Example `src/.env`:

```env
APP_NAME="mini-rag"
APP_VERSION="0.1"

FILE_ALLOWED_TYPE=["text/plain","application/pdf"]
FILE_ALLOWED_SIZE=10
FILE_DEFAULT_CHUNK_SIZE=512000

MONGODB_URL="mongodb://admin:admin@localhost:27007"
MONGODB_db="mini-rag"

GENERATION_BACKEND="OpenAI"
EMBEDING_BACKEND="Cohere"

OPENAI_API_KEY="your-openai-or-compatible-key"
OPENAI_API_URL="https://api.openai.com/v1"
COHERE_API_KEY="your-cohere-key"

GENERATION_MODEL_ID="gpt-4o-mini"
EMBEDDING_MODEL_ID="embed-multilingual-light-v3.0"
EMBEDDING_MODEL_SIZE=384

INPUT_DEFAULT_MAX_CHARACTERS=512
GENERATION_DEFAULT_MAX_TOKEN=1024
DEFAULT_TEMPERATURE=0.1

VECTOR_DB_BACKEND="Qdrant"
VECTOR_DB_PATH="qdrant_dir"
VECTOR_DISTANCE_METHOD="cosine"

PRIMARY_LANG="en"
DEFAULT_LANG="en"
```

### 6. Run the API

From `src/`:

```bash
uvicorn main:app --reload
```

Default docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Configuration Reference

### Core app settings

- `APP_NAME`: value returned by `/info/`
- `APP_VERSION`: value returned by `/info/`

### File ingestion settings

- `FILE_ALLOWED_TYPE`: allowed MIME types, currently expected to include text and PDF
- `FILE_ALLOWED_SIZE`: max upload size in MB
- `FILE_DEFAULT_CHUNK_SIZE`: upload read/write chunk size in bytes

### MongoDB settings

- `MONGODB_URL`: MongoDB connection string
- `MONGODB_db`: target database name

### LLM settings

- `GENERATION_BACKEND`: exact values currently wired in the factory are `OpenAI` and `Cohere`
- `EMBEDING_BACKEND`: exact values currently wired in the factory are `OpenAI` and `Cohere`
- `OPENAI_API_KEY`: used by the `OpenAI` provider
- `OPENAI_API_URL`: optional base URL for any OpenAI-compatible endpoint
- `COHERE_API_KEY`: used by the Cohere provider
- `GENERATION_MODEL_ID`: model used for text generation
- `EMBEDDING_MODEL_ID`: model used for embeddings
- `EMBEDDING_MODEL_SIZE`: vector dimension used when creating Qdrant collections
- `INPUT_DEFAULT_MAX_CHARACTERS`: prompt truncation limit before requests are sent
- `GENERATION_DEFAULT_MAX_TOKEN`: intended generation output token limit
- `DEFAULT_TEMPERATURE`: default generation temperature

### Vector DB settings

- `VECTOR_DB_BACKEND`: currently `Qdrant`
- `VECTOR_DB_PATH`: folder name created under `src/assets/database/`
- `VECTOR_DISTANCE_METHOD`: `cosine` or `dot`

### Prompt template settings

- `PRIMARY_LANG`: active prompt language
- `DEFAULT_LANG`: fallback prompt language

Supported prompt locales in the repository today:

- `en`
- `ar`

## Providers

### Generation providers

- `OpenAI`
- `Cohere`

### Embedding providers

- `OpenAI`
- `Cohere`

### Vector database

- `Qdrant`

Important note about Ollama:

- There is an `Ollama` enum in the codebase, but the factory does not currently instantiate a dedicated Ollama provider.
- The working way to use Ollama today is through the `OpenAI` provider by pointing `OPENAI_API_URL` to Ollama's OpenAI-compatible endpoint.

## Using Ollama via Docker with the OpenAI Provider

This project already supports OpenAI-compatible base URLs in `OpenAiProvider`, so Ollama works without adding a new provider class.

### 1. Start Ollama in Docker

```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama
```

### 2. Pull the model you want to use

Example generation model:

```bash
docker exec -it ollama ollama pull mistral:latest
```

If you also want embeddings through an OpenAI-compatible Ollama endpoint, pull an embedding model that your Ollama setup exposes and set `EMBEDDING_MODEL_SIZE` to that model's vector dimension.

### 3. Point the `OpenAI` provider to Ollama

Example: Ollama for generation, Cohere for embeddings

```env
GENERATION_BACKEND="OpenAI"
EMBEDING_BACKEND="Cohere"

OPENAI_API_KEY="ollama"
OPENAI_API_URL="http://localhost:11434/v1"
COHERE_API_KEY="your-cohere-key"

GENERATION_MODEL_ID="mistral:latest"
EMBEDDING_MODEL_ID="embed-multilingual-light-v3.0"
EMBEDDING_MODEL_SIZE=384
```

Example: Ollama for both generation and embeddings through the `OpenAI` provider

```env
GENERATION_BACKEND="OpenAI"
EMBEDING_BACKEND="OpenAI"

OPENAI_API_KEY="ollama"
OPENAI_API_URL="http://localhost:11434/v1"

GENERATION_MODEL_ID="mistral:latest"
EMBEDDING_MODEL_ID="your-embedding-model-name"
EMBEDDING_MODEL_SIZE=your_embedding_dimension
```

### 4. Networking notes

- If the API runs on your host machine, `http://localhost:11434/v1` is the right Ollama URL.
- If the API also runs in Docker, use the Ollama service hostname instead, for example `http://ollama:11434/v1`.
- The `OPENAI_API_KEY` value can be any non-empty string for local Ollama setups that do not enforce authentication.

## Data and Storage

The app creates and uses these storage locations:

- Uploaded files: `src/assets/files/<project_id>/`
- Local Qdrant data: `src/assets/database/<VECTOR_DB_PATH>/`

MongoDB collections created by the models:

- `projects`
- `assets`
- `chunks`

Qdrant collections are named like:

```text
project_<project_id>
```

`project_id` must be alphanumeric. The app auto-creates a project record the first time you use a new project ID.

## API Endpoints

OpenAPI is available at `/docs`, but the endpoint summary below is useful when wiring clients manually.

### 1. Service info

`GET /info/`

Example response:

```json
{
  "message": "mini-rag version 0.1"
}
```

### 2. Upload a file

`POST /api/v1/data/upload/{project_id}`

Request:

- `multipart/form-data`
- form field: `file`

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/data/upload/demo1" \
  -F "file=@/absolute/path/to/file.txt"
```

Example response:

```json
{
  "signal": "File uploaded successfully.",
  "file_id": "Ab12Cd34_file.txt",
  "asset_id": "68058f9c1f8f0d3ef80f7f0a"
}
```

### 3. Process uploaded files into chunks

`POST /api/v1/data/process/{project_id}`

Body fields:

- `file_id`: optional, process only one uploaded file
- `chunk_size`: optional, default `50`
- `ovelap_size`: optional, default `10`
- `do_reset`: optional, `1` deletes existing chunks for the project before inserting new ones

Note: the request field is spelled `ovelap_size` in the schema, so clients must send that exact name.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/data/process/demo1" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "Ab12Cd34_file.txt",
    "chunk_size": 500,
    "ovelap_size": 50,
    "do_reset": 1
  }'
```

If `file_id` is omitted, the endpoint processes all uploaded files for the project.

### 4. Push chunks into the vector index

Current registered route:

`POST /api/v1/nlpindex/push/{project_id}`

Body fields:

- `do_reset`: optional, `1` recreates the vector collection before indexing

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlpindex/push/demo1" \
  -H "Content-Type: application/json" \
  -d '{"do_reset": 1}'
```

### 5. Get vector collection info

Current registered route:

`GET /api/v1/nlpindex/info/{project_id}`

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/nlpindex/info/demo1"
```

### 6. Search the vector index

Current registered route:

`POST /api/v1/nlpindex/search/{project_id}`

Body fields:

- `query`: required
- `limit`: optional, default `5`

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlpindex/search/demo1" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this file about?",
    "limit": 5
  }'
```

Example response shape:

```json
{
  "signal": "Search in the vector database completed successfully.",
  "results": [
    {
      "score": 0.91,
      "text": "retrieved chunk text"
    }
  ]
}
```

### 7. Ask a RAG question

Current registered route:

`POST /api/v1/nlpindex/answer/{project_id}`

Body fields:

- `query`: required
- `limit`: optional, default `5`

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlpindex/answer/demo1" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize the main points.",
    "limit": 5
  }'
```

Example response shape:

```json
{
  "signal": "rag answer sucess",
  "answer": "generated answer",
  "full_prompt": "rendered retrieved-document prompt",
  "chat_history": [
    {
      "role": "system",
      "content": "Answer strictly based on the retrieved context only."
    }
  ]
}
```

## RAG Prompt Behavior

The bundled prompt templates instruct the model to:

- answer strictly from retrieved context
- avoid outside knowledge
- avoid hallucinations
- return a fallback answer when the context is insufficient

Prompt templates exist in:

- `src/stores/llms/templates/locales/en/rag.py`
- `src/stores/llms/templates/locales/ar/rag.py`

## Current Implementation Notes

These are worth knowing when you run the project as it exists today:

- The NLP router paths are currently registered as `/api/v1/nlpindex/...`, not `/api/v1/nlp/index/...`, because the route decorators in `src/routes/nlp.py` omit the leading slash.
- `GET /api/v1/nlpindex/info/{project_id}` currently returns HTTP `404` even when it includes a success payload with collection info.
- Upload validation allows PDF files, but the file processor compares against `ProcessingEnums.PDF` instead of `ProcessingEnums.PDF.value`, so PDF processing may fail until that code path is corrected.
- The exact env variable name is `EMBEDING_BACKEND` in the codebase.
- The `OpenAI` provider supports custom `OPENAI_API_URL`, which is why Ollama works here without a dedicated Ollama provider.
- In the current `LLmFactory`, the OpenAI provider's default output token setting is wired from `INPUT_DEFAULT_MAX_CHARACTERS` instead of `GENERATION_DEFAULT_MAX_TOKEN`.

## Troubleshooting

- If the app cannot find settings, make sure you started `uvicorn` from `src/` so `.env` is discovered.
- If MongoDB connection fails, verify the container is running on port `27007` and that the credentials in `src/.env` match the compose environment.
- If vector search fails on collection creation, make sure `EMBEDDING_MODEL_SIZE` matches the actual dimension returned by your embedding model.
- If Ollama generation fails, verify the model has been pulled inside the container and `OPENAI_API_URL` ends with `/v1`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
