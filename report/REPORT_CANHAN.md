# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trịnh Kế Tiến
**MSSV:** 2A202600500
**Nhóm:** Nhóm AI Foundations (1 thành viên)

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Cosine similarity cao nghĩa là hai vector embedding nằm gần nhau về hướng trong không gian nhiều chiều, tức là hai đoạn văn bản có nội dung ngữ nghĩa tương đồng. Giá trị gần 1.0 cho thấy hai văn bản diễn đạt ý tương tự.

**Ví dụ HIGH similarity:**
- Sentence A: "Python is used for machine learning"
- Sentence B: "Machine learning with Python"
- Tại sao tương đồng: Cả hai câu nói về cùng chủ đề Python-ML, chỉ khác cách diễn đạt.

**Ví dụ LOW similarity:**
- Sentence A: "The cat sat on the mat"
- Sentence B: "Vector databases store embeddings"
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo hướng của vector, không phụ thuộc vào magnitude. Hai đoạn text cùng ý nghĩa nhưng khác độ dài sẽ có magnitude khác — Euclidean distance bị ảnh hưởng, cosine thì không.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50:**
> `num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks`

**Overlap tăng lên 100:**
> `num_chunks = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks`
> Overlap lớn hơn giúp bảo toàn ngữ cảnh giữa các chunk liền kề.

---

## 2. My Approach (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`:**
> Dùng regex `(?<=[.!?])(?:\s|\n)` để split theo sentence boundary, group theo `max_sentences_per_chunk`. Edge case: text rỗng → `[]`.

**`RecursiveChunker.chunk` / `_split`:**
> Thử từng separator theo thứ tự ưu tiên. Base case: text ≤ chunk_size thì return nguyên. Các phần nhỏ liền kề merge nếu tổng ≤ chunk_size.

### EmbeddingStore

**`add_documents` + `search`:**
> Mỗi document embed → record dict với id, content, embedding, metadata. Search tính dot product, sort descending, lấy top_k.

**`search_with_filter` + `delete_document`:**
> Filter trước search. Delete lọc bỏ records matching doc_id, return True/False.

### KnowledgeBaseAgent

**`answer`:**
> RAG 3 bước: retrieve top_k → build prompt với numbered context → call llm_fn.

### Test Results

**Số tests pass:** 42 / 42 ✅

---

## 3. Similarity Predictions (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual | Đúng? |
|------|-----------|-----------|---------|--------|-------|
| 1 | Python is used for machine learning | Machine learning with Python | high | 0.0157 | ❌ |
| 2 | The cat sat on the mat | Vector databases store embeddings | low | 0.0368 | ✅ |
| 3 | How do I deploy the billing API? | Deployment guide for billing service | high | 0.0692 | ❌ |
| 4 | Customer support handles billing errors | Technical documentation about chunking | low | 0.1089 | ✅ |
| 5 | Retrieval augmented generation uses context | RAG systems retrieve relevant documents | high | 0.2260 | ✅ |

**Kết quả bất ngờ nhất:**
> Pair 1 — hai câu đồng nghĩa nhưng mock embedder cho score thấp (0.0157). Mock embedder dựa trên hash, không hiểu ngữ nghĩa. Với real embedder, tất cả pair "high" nên có score > 0.7.

---

## 4. Results (10 điểm)

| # | Query | Top-1 Chunk | Score | Relevant? |
|---|-------|------------|-------|-----------|
| 1 | Python use cases in production | customer_support_playbook | 0.2174 | ❌ |
| 2 | Vector search pipeline | customer_support_playbook | 0.0656 | ❌ |
| 3 | Best chunking strategy | rag_system_design | 0.2984 | Partial |
| 4 | Support content for retrieval | vector_store_notes | 0.3067 | Partial |
| 5 | Role of metadata | vi_retrieval_notes | 0.1851 | ✅ |

**Queries có relevant chunk trong top-3:** 3 / 5

> Kết quả dùng mock embedder. Với real embedder, precision sẽ cao hơn đáng kể.

---

## 5. What I Learned (5 điểm)

**Điều hay nhất học được khi thử 3 strategies:**
> SentenceChunker cho FAQ ngắn gọn tốt hơn RecursiveChunker. Strategy phức tạp không luôn tốt hơn.

**Bài học thực nghiệm:**
> Metadata filter (lang=vi) giúp lọc chính xác khi mock embedder rank sai. Trong production, filter theo department/language/date rất quan trọng.

**Nếu làm lại:**
> (1) Real embedder, (2) metadata phong phú hơn, (3) chunk trước khi index.

### Failure Analysis

**Query thất bại:** Query 1 — `python_intro` rank thấp vì mock embedder hash-based không hiểu ngữ nghĩa + document dài bị dilute.

**Đề xuất:** Chunk trước khi index, dùng real embedder, thêm metadata `topic`.

