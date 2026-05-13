# -*- coding: utf-8 -*-
"""Benchmark script to collect data for report."""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from src.chunking import (
    FixedSizeChunker, SentenceChunker, RecursiveChunker,
    compute_similarity, ChunkingStrategyComparator,
)
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

# ── 1. Load documents ──────────────────────────────────────
DATA_DIR = Path("data")
files = sorted(DATA_DIR.glob("*.txt")) + sorted(DATA_DIR.glob("*.md"))
files = [f for f in files if f.name != ".gitkeep"]

docs = []
for f in files:
    content = f.read_text(encoding="utf-8")
    doc = Document(
        id=f.stem,
        content=content,
        metadata={
            "source": str(f),
            "extension": f.suffix,
            "category": "technical" if f.suffix == ".md" else "general",
            "lang": "vi" if "vi_" in f.name else "en",
        }
    )
    docs.append(doc)

print("=" * 60)
print("DATA INVENTORY")
print("=" * 60)
for i, doc in enumerate(docs, 1):
    print(f"| {i} | {doc.id} | {doc.metadata['source']} | {len(doc.content)} | category={doc.metadata['category']}, lang={doc.metadata['lang']} |")

# ── 2. Chunking Strategy Comparison ────────────────────────
print("\n" + "=" * 60)
print("CHUNKING STRATEGY COMPARISON")
print("=" * 60)

comparator = ChunkingStrategyComparator()
for doc in docs[:3]:  # Compare on first 3 docs
    print(f"\n--- {doc.id} (len={len(doc.content)}) ---")
    result = comparator.compare(doc.content, chunk_size=200)
    for name, stats in result.items():
        print(f"  {name}: count={stats['count']}, avg_length={stats['avg_length']}")

# ── 3. Cosine Similarity Predictions ───────────────────────
print("\n" + "=" * 60)
print("COSINE SIMILARITY EXPERIMENTS")
print("=" * 60)

pairs = [
    ("Python is used for machine learning", "Machine learning with Python"),
    ("The cat sat on the mat", "Vector databases store embeddings"),
    ("How do I deploy the billing API?", "Deployment guide for billing service"),
    ("Customer support handles billing errors", "Technical documentation about chunking"),
    ("Retrieval augmented generation uses context", "RAG systems retrieve relevant documents"),
]

for i, (a, b) in enumerate(pairs, 1):
    vec_a = _mock_embed(a)
    vec_b = _mock_embed(b)
    score = compute_similarity(vec_a, vec_b)
    print(f"Pair {i}: score={score:.4f}")
    print(f"  A: {a}")
    print(f"  B: {b}")

# ── 4. Build store and run benchmark queries ───────────────
print("\n" + "=" * 60)
print("BENCHMARK QUERIES")
print("=" * 60)

store = EmbeddingStore(collection_name="benchmark_store", embedding_fn=_mock_embed)
store.add_documents(docs)
print(f"Store size: {store.get_collection_size()}")

benchmark_queries = [
    ("What are the main use cases of Python in production?", "Python is used for APIs, data pipelines, internal tools, and model-serving layers"),
    ("How does a vector search pipeline work?", "Chunk documents, embed chunks, store vectors with metadata, embed query and rank by similarity"),
    ("What chunking strategy performed best in the experiment?", "Recursive chunking offered the best balance in the experiment"),
    ("How should customer support content be written for retrieval?", "Authors should specify exact page, button, or log source instead of vague statements"),
    ("What is the role of metadata in retrieval systems?", "Metadata helps filter search space by department, language, date, etc. to improve precision"),
]

def demo_llm(prompt: str) -> str:
    return f"[Answer based on retrieved context]"

agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

for i, (query, gold) in enumerate(benchmark_queries, 1):
    results = store.search(query, top_k=3)
    answer = agent.answer(query, top_k=3)
    print(f"\nQuery {i}: {query}")
    print(f"Gold: {gold}")
    for j, r in enumerate(results, 1):
        content_preview = r['content'][:100].replace('\n', ' ')
        print(f"  Top-{j}: score={r['score']:.4f} | {content_preview}...")
    print(f"  Agent answer: {answer[:150]}...")

# ── 5. Filtered search test ────────────────────────────────
print("\n" + "=" * 60)
print("METADATA FILTER TEST")
print("=" * 60)

filtered = store.search_with_filter("retrieval quality", top_k=3, metadata_filter={"lang": "vi"})
print(f"Filter lang=vi, query='retrieval quality': {len(filtered)} results")
for r in filtered:
    print(f"  score={r['score']:.4f} | {r['content'][:80].replace(chr(10), ' ')}...")

unfiltered = store.search("retrieval quality", top_k=3)
print(f"\nUnfiltered: {len(unfiltered)} results")
for r in unfiltered:
    print(f"  score={r['score']:.4f} | {r['content'][:80].replace(chr(10), ' ')}...")

# ── 6. Delete test ────────────────────────────────────────
print("\n" + "=" * 60)
print("DELETE TEST")
print("=" * 60)
size_before = store.get_collection_size()
deleted = store.delete_document("python_intro")
size_after = store.get_collection_size()
print(f"Before: {size_before}, Deleted python_intro: {deleted}, After: {size_after}")

print("\n✅ Benchmark complete!")
