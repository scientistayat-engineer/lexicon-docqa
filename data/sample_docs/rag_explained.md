# Retrieval-Augmented Generation (RAG)
RAG combines a retriever with a language model. First the user's question is converted into an embedding and used to retrieve the most relevant chunks from a vector database. Then those chunks are placed in the prompt as context, and the LLM writes an answer grounded in them.

RAG reduces hallucination because the model answers from retrieved evidence instead of memory alone. It also lets a system use private or recent documents without retraining the model.

Good RAG depends on chunking, embedding quality, the number of retrieved chunks (top-k) and a prompt that tells the model to stay within the context.
