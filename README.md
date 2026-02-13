# GEN-AI-Notes: Python Gen AI POC Repository

A comprehensive collection of Proof of Concept (POC) implementations for Python-based Generative AI applications, progressing from beginner to expert level.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing LLM-powered applications
- **LangGraph**: Library for building stateful, multi-agent applications
- **Pydantic**: Data validation using Python type annotations
- **ElasticAPM**: Application Performance Monitoring
- **OpenAI**: LLM and embedding models
- **FAISS**: Efficient similarity search and vector storage

## Repository Structure

```
GEN-AI-Notes/
├── beginner/          # POCs 1-5
├── intermediate/      # POCs 6-12
├── advanced/          # POCs 13-20
├── expert/            # POCs 21-30
├── shared/            # Shared utilities and configs
└── docs/              # Documentation
```

---

## POC Roadmap

### BEGINNER LEVEL (1-5)

#### 1. Basic FastAPI + OpenAI Integration
- Simple REST API with OpenAI chat completion
- Pydantic models for request/response validation
- Basic error handling
- **Tech**: FastAPI, OpenAI, Pydantic
- **Status**: ✅ Completed
- **Location**: `beginner/poc-01-basic-fastapi-openai/`

#### 2. Simple LangChain Chatbot
- Basic conversation chain with memory
- Prompt templates
- Chat history management
- **Tech**: FastAPI, LangChain, OpenAI, Pydantic
- **Status**: ✅ Completed
- **Location**: `beginner/poc-02-simple-langchain-chatbot/`

#### 3. Document QA with FAISS
- Load documents and create embeddings
- Basic similarity search
- Simple question-answering endpoint
- **Tech**: FastAPI, LangChain, FAISS, OpenAI
- **Status**: ✅ Completed
- **Location**: `beginner/poc-03-document-qa-faiss/`

#### 4. Pydantic AI Response Structuring
- Structured output extraction from LLM
- Function calling with OpenAI
- Data validation and parsing
- **Tech**: FastAPI, OpenAI, Pydantic
- **Status**: ✅ Completed
- **Location**: `beginner/poc-04-pydantic-ai-structuring/`

#### 5. Basic APM Integration
- ElasticAPM setup with FastAPI
- Request tracing
- Performance monitoring basics
- **Tech**: FastAPI, ElasticAPM
- **Status**: ✅ Completed
- **Location**: `beginner/poc-05-basic-apm-integration/`

---

### INTERMEDIATE LEVEL (6-12)

#### 6. RAG System with Multiple Document Types
- Support PDF, TXT, DOCX, Markdown
- Document chunking strategies
- Metadata filtering
- **Tech**: LangChain, FAISS, OpenAI, FastAPI
- **Status**: ✅ Completed
- **Location**: `intermediate/poc-06-rag-multi-document-types/`

#### 7. Conversational RAG with Memory
- Chat history + RAG retrieval
- Context-aware responses
- Session management
- **Tech**: LangChain, FAISS, OpenAI, FastAPI, Pydantic
- **Status**: ✅ Completed
- **Location**: `intermediate/poc-07-conversational-rag-memory/`

#### 8. LangChain Agents with Tools
- Custom tool creation
- ReAct agent implementation
- Tool selection and execution
- **Tech**: LangChain, OpenAI, FastAPI, Pydantic
- **Status**: ⬜ Not Started

#### 9. Multi-Query RAG System
- Query expansion and transformation
- Multiple retrieval strategies
- Result fusion and ranking
- **Tech**: LangChain, FAISS, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 10. Streaming Responses
- Server-Sent Events (SSE) for streaming
- Token-by-token streaming from OpenAI
- Progress indicators
- **Tech**: FastAPI, LangChain, OpenAI
- **Status**: ⬜ Not Started

#### 11. Document Summarization Pipeline
- Map-reduce summarization
- Hierarchical summarization
- Custom prompts per document type
- **Tech**: LangChain, OpenAI, FastAPI, Pydantic
- **Status**: ⬜ Not Started

#### 12. Vector Store Comparison
- Multiple vector stores (FAISS, Chroma, in-memory)
- Performance benchmarking
- Trade-offs analysis
- **Tech**: LangChain, FAISS, OpenAI
- **Status**: ⬜ Not Started

---

### ADVANCED LEVEL (13-20)

#### 13. LangGraph Multi-Agent Workflow
- State management with LangGraph
- Multiple specialized agents
- Conditional routing
- **Tech**: LangGraph, LangChain, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 14. Advanced RAG with Hybrid Search
- Combine semantic + keyword search
- Re-ranking strategies
- Query routing
- **Tech**: LangChain, FAISS, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 15. Agentic RAG System
- Self-querying retriever
- Adaptive retrieval strategies
- Routing to different data sources
- **Tech**: LangGraph, LangChain, FAISS, OpenAI
- **Status**: ⬜ Not Started

#### 16. Production-Ready APM Integration
- Custom ElasticAPM spans
- Distributed tracing
- Error tracking and alerting
- Performance metrics for LLM calls
- **Tech**: FastAPI, ElasticAPM, LangChain, OpenAI
- **Status**: ⬜ Not Started

#### 17. Caching and Optimization Layer
- Semantic caching with FAISS
- LRU cache for common queries
- Response deduplication
- Cost optimization
- **Tech**: FastAPI, LangChain, FAISS, Redis (optional)
- **Status**: ⬜ Not Started

#### 18. Multi-Modal RAG System
- Image + text processing
- Vision models integration
- Multi-modal embeddings
- **Tech**: LangChain, FAISS, OpenAI (GPT-4 Vision), FastAPI
- **Status**: ⬜ Not Started

#### 19. Dynamic Prompt Engineering System
- Prompt versioning and A/B testing
- Template management
- Performance tracking per prompt
- **Tech**: LangChain, OpenAI, FastAPI, Pydantic
- **Status**: ⬜ Not Started

#### 20. Guardrails and Content Moderation
- Input/output validation
- PII detection and masking
- Toxic content filtering
- Custom safety checks
- **Tech**: LangChain, OpenAI, FastAPI, Pydantic
- **Status**: ⬜ Not Started

---

### EXPERT LEVEL (21-30)

#### 21. LangGraph Complex Workflow Engine
- Multi-step reasoning chains
- Human-in-the-loop approval
- State persistence and resume
- Cycle detection and handling
- **Tech**: LangGraph, LangChain, OpenAI, FastAPI, Pydantic
- **Status**: ⬜ Not Started

#### 22. Advanced Agent Orchestration
- Hierarchical agent teams
- Manager-worker pattern
- Task delegation and aggregation
- **Tech**: LangGraph, LangChain, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 23. Custom Embedding Pipeline
- Fine-tuned embeddings
- Domain-specific embeddings
- Embedding compression
- Multi-language support
- **Tech**: LangChain, FAISS, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 24. Retrieval Performance Optimization
- FAISS index optimization (IVF, HNSW)
- Quantization strategies
- Distributed retrieval
- Benchmarking suite
- **Tech**: FAISS, LangChain, FastAPI
- **Status**: ⬜ Not Started

#### 25. Observability and Monitoring Stack
- End-to-end tracing
- LLM call analytics
- Cost tracking per request
- Quality metrics (hallucination detection)
- Custom ElasticAPM dashboards
- **Tech**: ElasticAPM, FastAPI, LangChain, OpenAI
- **Status**: ⬜ Not Started

#### 26. Evaluation and Testing Framework
- Automated RAG evaluation (RAGAS)
- Prompt testing suite
- Regression testing for LLM outputs
- Quality scoring system
- **Tech**: LangChain, OpenAI, FastAPI, Pydantic
- **Status**: ⬜ Not Started

#### 27. Production RAG with Advanced Features
- Incremental index updates
- Multi-tenancy support
- Role-based access control
- Document versioning
- Audit logging
- **Tech**: FastAPI, LangChain, FAISS, ElasticAPM, Pydantic
- **Status**: ⬜ Not Started

#### 28. Custom LangGraph Extensions
- Custom state managers
- Advanced checkpointing
- Distributed execution
- Time travel debugging
- **Tech**: LangGraph, LangChain, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 29. Adaptive Learning System
- User feedback loop
- Dynamic retrieval optimization
- Prompt refinement based on outcomes
- A/B testing infrastructure
- **Tech**: LangGraph, LangChain, FAISS, OpenAI, FastAPI
- **Status**: ⬜ Not Started

#### 30. Enterprise-Grade Gen AI Platform
- Complete integration of all technologies
- Microservices architecture
- Load balancing and scaling
- Disaster recovery
- Comprehensive monitoring
- Security hardening
- **Tech**: All (FastAPI, LangChain, LangGraph, FAISS, OpenAI, ElasticAPM, Pydantic)
- **Status**: ⬜ Not Started

---

## Suggested Learning Path

### Phase 1: Foundation (Weeks 1-2)
1. POC 1: Basic FastAPI + OpenAI Integration
2. POC 2: Simple LangChain Chatbot
3. POC 3: Document QA with FAISS

### Phase 2: Monitoring & Structure (Week 3)
4. POC 5: Basic APM Integration
5. POC 4: Pydantic AI Response Structuring

### Phase 3: Advanced RAG (Weeks 4-6)
6. POC 6: RAG System with Multiple Document Types
7. POC 7: Conversational RAG with Memory
8. POC 9: Multi-Query RAG System

### Phase 4: Agents & Workflows (Weeks 7-8)
9. POC 8: LangChain Agents with Tools
10. POC 13: LangGraph Multi-Agent Workflow

### Phase 5: Production Features (Weeks 9-10)
11. POC 10: Streaming Responses
12. POC 16: Production-Ready APM Integration
13. POC 17: Caching and Optimization Layer

### Phase 6: Expert Topics (Weeks 11+)
14. Continue with advanced and expert level POCs based on specific needs

---

## Getting Started

### Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies (once requirements.txt is created)
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
ELASTIC_APM_SERVER_URL=your_apm_server_url
ELASTIC_APM_SERVICE_NAME=gen-ai-pocs
```

### Running a POC

```bash
# Navigate to specific POC directory
cd beginner/poc-01-basic-fastapi-openai

# Run the FastAPI application
uvicorn main:app --reload
```

---

## Project Goals

- **Learn by Doing**: Hands-on implementation of Gen AI concepts
- **Progressive Complexity**: Build skills incrementally from basics to advanced
- **Production-Ready**: Include monitoring, error handling, and best practices
- **Reusable Components**: Create modular, maintainable code
- **Documentation**: Clear explanations and code comments

---

## Contributing

Each POC should include:
- `README.md`: Explanation of the concept and implementation
- `main.py`: Core application code
- `requirements.txt`: Specific dependencies
- `tests/`: Unit and integration tests
- `.env.example`: Example environment variables

---

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FAISS Documentation](https://faiss.ai/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Elastic APM Documentation](https://www.elastic.co/guide/en/apm/agent/python/current/index.html)

---

## License

MIT License - Feel free to use these POCs for learning and development.

---

## Progress Tracking

**Total POCs**: 30
**Completed**: 6
**In Progress**: 0
**Not Started**: 24

**Last Updated**: 2025-11-15

### Completed POCs
1. ✅ POC 1: Basic FastAPI + OpenAI Integration (`beginner/poc-01-basic-fastapi-openai/`)
2. ✅ POC 2: Simple LangChain Chatbot (`beginner/poc-02-simple-langchain-chatbot/`)
3. ✅ POC 3: Document QA with FAISS (`beginner/poc-03-document-qa-faiss/`)
4. ✅ POC 4: Pydantic AI Response Structuring (`beginner/poc-04-pydantic-ai-structuring/`)
5. ✅ POC 5: Basic APM Integration (`beginner/poc-05-basic-apm-integration/`)
6. ✅ POC 6: RAG System with Multiple Document Types (`intermediate/poc-06-rag-multi-document-types/`)
