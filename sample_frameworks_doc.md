# AI Agent Frameworks Technical Specification

## LangGraph Architecture
LangGraph is a library designed for building stateful, multi-actor applications with LLMs, built by LangChain Inc.
It extends the core LangChain concepts with cyclic graphs, fine-grained state schemas, and persistent checkpointing.
Key features include:
- Cyclic graph workflows allowing agents to loop, critique, and self-correct.
- Built-in persistence for human-in-the-loop approvals and replayability.
- Multi-agent coordination patterns including supervisor architectures and peer-to-peer networks.
- Tight integration with PostgreSQL and pgvector for state persistence and vector memory.

## LangChain Framework
LangChain provides modular components for LLM applications.
- Extensive library of 700+ document loaders, retrievers, and tool integrations.
- Best for linear RAG chains and structured extraction.
- Graph state management is more verbose compared to dedicated graph orchestrators.

## AutoGPT
AutoGPT is an experimental open-source autonomous agent application.
- Employs autonomous prompt loops for multi-step web research and command execution.
- Susceptible to infinite loops and higher token costs without strict bounding.
- Requires sandboxed environments for safe code execution.

## Vector Storage with pgvector
pgvector adds vector similarity search capabilities directly to PostgreSQL.
- Supports cosine distance (<=>), L2 distance (<->), and inner product (<#>) operators.
- Eliminates external vector DB management overhead by storing relational metadata alongside embeddings.
