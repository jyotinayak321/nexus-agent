# NEXUS Autonomous Agent — RAG + Docker Starter

NEXUS now includes a working local-document RAG path:

`React -> FastAPI -> RAG retrieval (PostgreSQL + pgvector) -> LangGraph agents -> Groq/Mock LLM`

## What was added

- PDF/TXT/MD upload endpoint and frontend uploader
- PyMuPDF text extraction
- overlapping text chunking
- `sentence-transformers/all-MiniLM-L6-v2` embeddings (384 dimensions)
- PostgreSQL + pgvector persistence
- cosine-similarity retrieval
- retrieved context injected into the Research Agent before planning
- source metadata returned with the agent result
- Dockerfiles for frontend/backend
- `docker-compose.yml` with pgvector PostgreSQL

## Important project files

```text
nexus-agent-starter/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── rag_service.py
│   ├── llm_provider.py
│   ├── agents/
│   │   ├── graph.py
│   │   └── research_agent.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── src/
        ├── api.js
        └── components/KnowledgeBase.jsx
```

## Run with Docker (recommended)

Create your backend environment file first:

```bash
cp backend/.env.example backend/.env
```

Put a real `GROQ_API_KEY` in `backend/.env` if you want real LLM output. The default `GROQ_MODEL` is configurable through the same file; without a configured key, NEXUS uses the MockProvider so the rest of the pipeline can still be tested.

Then start everything:

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:5174`
- Backend docs: `http://localhost:8420/docs`
- Health: `http://localhost:8420/health`
- PostgreSQL host port: `55432`

First backend startup downloads the sentence-transformer embedding model and stores it in the `huggingface_cache` Docker volume.

## Run without Docker

Start PostgreSQL with pgvector available and use the URL from `.env.example`.

Backend:

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8420
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## RAG flow

1. Upload a `.pdf`, `.txt`, or `.md` file.
2. Backend extracts text and creates overlapping chunks.
3. Sentence Transformer converts each chunk to a 384-dimensional vector.
4. Chunks + vectors are saved in the `document_chunks` pgvector table.
5. When a goal runs, the goal text is embedded.
6. pgvector finds the closest chunks using cosine distance.
7. Those chunks are added to `rag_context`.
8. `research_agent.py` uses that retrieved context as primary evidence.
9. The remaining planning/risk/decision/execution/review nodes run normally.

## RAG API

### Upload document

```http
POST /documents/upload
Content-Type: multipart/form-data
file=<PDF/TXT/MD>
```

### List indexed documents

```http
GET /documents
```

### Test retrieval directly

```http
POST /rag/search
Content-Type: application/json

{
  "query": "What are the important project constraints?",
  "top_k": 5
}
```

### Execute a goal with RAG

The existing flow stays the same:

```text
POST /goal -> POST /execute/{goal_id}
```

`/execute` now automatically retrieves relevant local chunks and sends them into the LangGraph state before the Research Agent starts.

## Configuration

Useful `backend/.env` values:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_TOP_K=5
RAG_CHUNK_SIZE=900
RAG_CHUNK_OVERLAP=150
MAX_DOCUMENT_MB=20
```

The `DocumentChunk.embedding` column is currently fixed at **384 dimensions** to match `all-MiniLM-L6-v2`. If you change to an embedding model with a different dimension, update `EMBEDDING_DIMENSION` in `backend/models.py` and recreate/migrate that table.

## Recommended demo sequence

1. Start Docker Compose.
2. Upload your project/problem-statement PDF from the Knowledge Base section.
3. Use the Search box to prove retrieval is working.
4. Enter a goal related to that PDF.
5. Run NEXUS.
6. Show the retrieved source chips under the plan.
7. Explain that retrieval grounds the Research Agent, while LangGraph coordinates the downstream agents.
