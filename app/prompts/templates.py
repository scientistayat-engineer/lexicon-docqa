"""Part 1: three prompt templates (zero-shot, few-shot, role-based)."""

MODES = {"zero_shot": "Zero-shot", "few_shot": "Few-shot", "role_based": "Role-based"}

ZERO_SHOT = """Answer the question using the context below.

Context:
{context}

Question: {question}
Answer:"""

FEW_SHOT = """Answer the question using only the context. Follow the style of the examples.

Example 1
Context: Python lists are mutable sequences. Tuples are immutable sequences.
Question: What is the difference between a list and a tuple?
Answer: A list can be changed after creation, while a tuple cannot.

Example 2
Context: ChromaDB stores embeddings and supports similarity search.
Question: What does ChromaDB do?
Answer: It stores embeddings and finds the most similar ones to a query.

Example 3
Context: I don't know. (no relevant text)
Question: Who won the 2010 World Cup?
Answer: The documents do not contain this information.

Now your turn.
Context:
{context}

Question: {question}
Answer:"""

ROLE_SYSTEM = """You are a senior technical document analyst.
Rules:
1. Use ONLY the provided context. Never invent facts.
2. Start with a one-sentence direct answer, then add short supporting details.
3. Mention the source file names you relied on in brackets, e.g. [rag_explained.md].
4. If the context does not contain the answer, say so clearly."""

ROLE_USER = """Context:
{context}

Question: {question}"""


def build_messages(mode: str, question: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n".join(f"[{c['source']}] {c['text']}" for c in chunks) or "(no context found)"
    if mode == "zero_shot":
        return [{"role": "user", "content": ZERO_SHOT.format(context=context, question=question)}]
    if mode == "few_shot":
        return [{"role": "user", "content": FEW_SHOT.format(context=context, question=question)}]
    if mode == "role_based":
        return [{"role": "system", "content": ROLE_SYSTEM},
                {"role": "user", "content": ROLE_USER.format(context=context, question=question)}]
    raise ValueError(f"Unknown mode: {mode}")
