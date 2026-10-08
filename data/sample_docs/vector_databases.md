# Vector Databases
A vector database stores embeddings together with their original text and metadata, and answers nearest-neighbour queries quickly. Instead of matching keywords, it returns the items whose vectors are closest to the query vector.

ChromaDB is an open-source vector database that runs locally and can persist data to disk. FAISS is a library from Meta that indexes vectors for very fast similarity search. Both support cosine or Euclidean distance.

In a RAG pipeline the vector database is the memory: documents are chunked, embedded and stored once, then searched on every question.
