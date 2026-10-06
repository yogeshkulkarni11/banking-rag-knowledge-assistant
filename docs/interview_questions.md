# Interview Questions

## 1. Why use RAG?
RAG separates knowledge from model weights. Documents can be updated and retrieved at runtime, while the LLM focuses on reasoning over supplied evidence.

## 2. What happens during ingestion?
Documents are loaded, split into semantic chunks, embedded, and stored with metadata in a vector database.

## 3. What happens during retrieval?
The user question is embedded into the same vector space. ChromaDB returns the nearest chunks using vector similarity.

## 4. Why keep source metadata?
Metadata enables traceability, citations, filtering, and debugging of poor retrieval.

## 5. What is chunking?
Chunking divides large documents into smaller retrieval units. Smaller chunks can improve precision, while overly small chunks can lose context.

## 6. What is top-K retrieval?
Top-K retrieval selects the K most similar chunks to provide relevant context without sending the entire corpus to the LLM.

## 7. How would you improve this project for production?
Use Azure AI Search, Azure OpenAI, Key Vault, document-level ACL filters, hybrid/vector search, reranking, prompt-injection defenses, evaluation datasets, observability, and automated index refresh.

## 8. How do you reduce hallucination?
Restrict the prompt to retrieved evidence, require citations, return an explicit insufficient-context response, and evaluate groundedness and retrieval quality.
