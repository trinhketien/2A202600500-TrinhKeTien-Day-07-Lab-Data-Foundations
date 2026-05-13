# Báo Cáo Lab 7: Embedding & Vector Store

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
- Tại sao tương đồng: Cả hai câu đều nói về cùng chủ đề — mối quan hệ giữa Python và machine learning, chỉ khác cách diễn đạt.

**Ví dụ LOW similarity:**
- Sentence A: "The cat sat on the mat"
- Sentence B: "Vector databases store embeddings"
- Tại sao khác: Hai câu thuộc hoàn toàn hai lĩnh vực khác nhau — một câu về động vật, một câu về công nghệ lưu trữ dữ liệu.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo hướng của vector, không phụ thuộc vào độ dài (magnitude). Điều này quan trọng vì hai đoạn text có cùng ý nghĩa nhưng khác độ dài sẽ tạo ra vector có magnitude khác nhau — Euclidean distance sẽ bị ảnh hưởng bởi sự khác biệt này, trong khi cosine similarity vẫn cho kết quả chính xác.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
> `num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23 chunks`

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> `num_chunks = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks`
> Overlap nhiều hơn tạo ra thêm 2 chunks. Overlap lớn hơn giúp bảo toàn ngữ cảnh giữa các chunk liền kề — nếu một câu hoặc ý nằm ở ranh giới hai chunk, overlap đảm bảo cả hai chunk đều chứa phần thông tin chuyển tiếp đó.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** AI Engineering — Knowledge Assistant & RAG Systems

**Tại sao chọn domain này?**
> Chọn domain AI Engineering vì nó trực tiếp liên quan đến nội dung lab — embedding, vector store, và RAG. Bộ tài liệu bao gồm cả tiếng Anh và tiếng Việt, cho phép kiểm tra khả năng retrieval đa ngôn ngữ. Các tài liệu đa dạng từ coding guides, system design, đến support playbook giúp kiểm tra nhiều kịch bản retrieval khác nhau.

### Phân Công Công Việc

| Phase | Công việc | Phụ trách |
|-------|----------|----------|
| Phase 1 — Cá nhân | Implement src package (chunking, store, agent) | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Chọn domain & thu thập tài liệu | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Thiết kế metadata schema | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Viết 5 benchmark queries + gold answers | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Chạy benchmark & phân tích kết quả | Trịnh Kế Tiến |
| Phase 2 — Nhóm | So sánh strategy & failure analysis | Trịnh Kế Tiến |

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | customer_support_playbook | data/customer_support_playbook.txt | 1,692 | category=general, lang=en |
| 2 | python_intro | data/python_intro.txt | 1,944 | category=general, lang=en |
| 3 | chunking_experiment_report | data/chunking_experiment_report.md | 1,987 | category=technical, lang=en |
| 4 | rag_system_design | data/rag_system_design.md | 2,391 | category=technical, lang=en |
| 5 | vector_store_notes | data/vector_store_notes.md | 2,123 | category=technical, lang=en |
| 6 | vi_retrieval_notes | data/vi_retrieval_notes.md | 1,667 | category=technical, lang=vi |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| category | string | "technical" / "general" | Phân loại tài liệu kỹ thuật vs tổng hợp, giúp filter khi user hỏi câu hỏi chuyên sâu |
| lang | string | "en" / "vi" | Lọc theo ngôn ngữ, tránh trả về tài liệu tiếng Việt khi user hỏi tiếng Anh và ngược lại |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu (chunk_size=200):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| customer_support_playbook | FixedSizeChunker | 11 | 199.27 | Trung bình — cắt giữa câu |
| customer_support_playbook | SentenceChunker | 4 | 421.0 | Tốt — giữ nguyên câu |
| customer_support_playbook | RecursiveChunker | 14 | 119.07 | Tốt — tách theo paragraph |
| python_intro | FixedSizeChunker | 13 | 195.69 | Trung bình |
| python_intro | SentenceChunker | 5 | 387.0 | Tốt |
| python_intro | RecursiveChunker | 14 | 136.93 | Tốt |
| chunking_experiment_report | FixedSizeChunker | 13 | 199.0 | Trung bình |
| chunking_experiment_report | SentenceChunker | 5 | 395.6 | Tốt |
| chunking_experiment_report | RecursiveChunker | 18 | 108.44 | Rất tốt — tách theo heading |

### Strategy Của Tôi

**Loại:** RecursiveChunker (tuned: chunk_size=300)

**Mô tả cách hoạt động:**
> RecursiveChunker thử tách text bằng các separator theo thứ tự ưu tiên: `\n\n` (paragraph) → `\n` (newline) → `. ` (sentence) → ` ` (word) → `""` (character). Khi gặp separator đầu tiên có thể tách text, nó chia thành các phần nhỏ. Nếu phần nào vẫn lớn hơn chunk_size, nó đệ quy xuống separator tiếp theo. Cuối cùng, các phần nhỏ liền kề được merge lại nếu tổng kích thước vẫn nằm trong giới hạn.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Domain AI Engineering có tài liệu dạng markdown với cấu trúc rõ ràng: heading, paragraph, bullet points. RecursiveChunker khai thác cấu trúc này bằng cách ưu tiên tách theo paragraph boundary trước, giữ nguyên ý hoàn chỉnh trong mỗi chunk. Điều này đặc biệt hiệu quả cho tài liệu kỹ thuật có nhiều section.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|-------------------|
| chunking_experiment_report | best baseline (SentenceChunker) | 5 | 395.6 | Tốt nhưng chunk dài |
| chunking_experiment_report | **RecursiveChunker (của tôi)** | 18 | 108.44 | Chunk ngắn gọn, đúng section |

### So Sánh Giữa Các Strategy (tự thử nghiệm)

> *Nhóm chỉ có 1 thành viên, nên tôi tự thử cả 3 strategy trên cùng bộ tài liệu để so sánh.*

| Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|----------|----------------------|-----------|----------|
| RecursiveChunker (300) | 7/10 | Giữ cấu trúc paragraph, linh hoạt | Chunk có thể quá nhỏ |
| SentenceChunker (3) | 6/10 | Chunk đọc tự nhiên | Chunk dài, pha trộn ý |
| FixedSizeChunker (200) | 5/10 | Đơn giản, dự đoán được | Cắt giữa câu |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> RecursiveChunker phù hợp nhất cho domain AI Engineering vì tài liệu có cấu trúc markdown rõ ràng. Nó tôn trọng ranh giới paragraph và heading, giúp mỗi chunk giữ được một ý trọn vẹn. SentenceChunker là lựa chọn thay thế tốt cho FAQ ngắn gọn.

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex `(?<=[.!?])(?:\s|\n)` để detect ranh giới câu — split sau dấu `.`, `!`, `?` khi theo sau bởi whitespace hoặc newline. Sau đó group các câu theo `max_sentences_per_chunk` bằng slicing. Edge case: text rỗng trả về `[]`, câu cuối không cần kết thúc bằng dấu câu.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Algorithm thử từng separator theo thứ tự ưu tiên. Nếu separator không split được (chỉ 1 phần), chuyển sang separator tiếp theo. Base case: text ≤ chunk_size thì return nguyên, hoặc hết separator thì force split theo character. Các phần nhỏ liền kề được merge nếu tổng ≤ chunk_size.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi document được embed bằng `embedding_fn`, lưu thành record dict chứa `id`, `doc_id`, `content`, `embedding`, `metadata`. Search embed query rồi tính dot product với tất cả stored embeddings, sort descending và lấy top_k. Hỗ trợ cả ChromaDB backend và in-memory fallback.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter`: filter trước — lọc records có metadata match tất cả key-value trong filter dict, sau đó search trên tập đã lọc. `delete_document`: lọc ra tất cả records không có `doc_id` matching, trả về `True` nếu size giảm, `False` nếu không tìm thấy.

### KnowledgeBaseAgent

**`answer`** — approach:
> RAG pattern 3 bước: (1) search top_k chunks từ store, (2) build prompt bằng cách đánh số mỗi chunk `[1]`, `[2]`, `[3]` trong phần Context, kèm câu hỏi, (3) gọi `llm_fn(prompt)` và return kết quả. Prompt structure rõ ràng giúp LLM phân biệt context vs question.

### Test Results

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.97s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is used for machine learning | Machine learning with Python | high | 0.0157 | ❌ |
| 2 | The cat sat on the mat | Vector databases store embeddings | low | 0.0368 | ✅ |
| 3 | How do I deploy the billing API? | Deployment guide for billing service | high | 0.0692 | ❌ |
| 4 | Customer support handles billing errors | Technical documentation about chunking | low | 0.1089 | ✅ |
| 5 | Retrieval augmented generation uses context | RAG systems retrieve relevant documents | high | 0.2260 | ✅ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Pair 1 bất ngờ nhất — hai câu gần như đồng nghĩa nhưng mock embedder cho score rất thấp (0.0157). Điều này cho thấy mock embedder dựa trên hash, không hiểu ngữ nghĩa thực sự. Với embedder thật (như all-MiniLM-L6-v2), kết quả sẽ phản ánh đúng hơn. Pair 5 có score cao nhất (0.2260) vì ngẫu nhiên hash tạo ra vector gần nhau hơn — nhưng trong thực tế, tất cả pair "high" đều nên có score > 0.7 với real embedder.

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What are the main use cases of Python in production? | Python is used for APIs, data pipelines, internal tools, and model-serving layers |
| 2 | How does a vector search pipeline work? | Chunk documents, embed chunks, store vectors with metadata, embed query and rank by similarity |
| 3 | What chunking strategy performed best in the experiment? | Recursive chunking offered the best balance in the experiment |
| 4 | How should customer support content be written for retrieval? | Authors should specify exact page, button, or log source instead of vague statements |
| 5 | What is the role of metadata in retrieval systems? | Metadata helps filter search space by department, language, date, etc. to improve precision |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Python use cases in production | customer_support_playbook | 0.2174 | ❌ | Context từ support playbook, không đúng target |
| 2 | Vector search pipeline | customer_support_playbook | 0.0656 | ❌ | Context không chứa vector pipeline info |
| 3 | Best chunking strategy | rag_system_design | 0.2984 | Partial | RAG design có đề cập chunking, nhưng không phải experiment report |
| 4 | Support content for retrieval | vector_store_notes | 0.3067 | Partial | Vector store notes có liên quan, nhưng customer_support (top-2) phù hợp hơn |
| 5 | Role of metadata | vi_retrieval_notes | 0.1851 | ✅ | vi_retrieval_notes nói rõ về metadata filtering |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

> **Ghi chú:** Kết quả dùng mock embedder (hash-based, không hiểu ngữ nghĩa). Với real embedder, retrieval precision sẽ cao hơn đáng kể. Mock embedder phù hợp cho testing code logic, nhưng không phản ánh chất lượng retrieval thực tế.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được khi tự thử nghiệm 3 strategies:**
> Khi thử SentenceChunker, tôi nhận ra rằng với FAQ ngắn gọn, chunking theo câu cho kết quả đọc dễ hiểu hơn RecursiveChunker. Không phải lúc nào strategy phức tạp hơn cũng tốt hơn — phụ thuộc vào cấu trúc tài liệu.

**Bài học từ quá trình thực nghiệm:**
> Khi thử metadata filter theo ngôn ngữ (lang=vi), tôi phát hiện rằng tài liệu tiếng Việt bị rank thấp hơn vì mock embedder không hiểu ngữ nghĩa. Trong production, metadata filtering giúp giải quyết vấn đề này — lọc theo department, language, hoặc freshness date.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ (1) dùng real embedder thay vì mock để đánh giá retrieval quality chính xác hơn, (2) thêm metadata phong phú hơn (date, author, difficulty level), và (3) chunk tài liệu trước khi lưu vào store thay vì lưu nguyên document — điều này sẽ cải thiện retrieval precision đáng kể vì mỗi chunk chỉ chứa một ý.

### Failure Analysis

**Query thất bại:** Query 1 ("What are the main use cases of Python in production?")

**Tại sao thất bại?**
> Mock embedder không hiểu ngữ nghĩa — hash-based embedding tạo ra vector ngẫu nhiên, nên document `python_intro` (chứa đúng câu trả lời) lại rank thấp hơn `customer_support_playbook` (không liên quan). Ngoài ra, tài liệu được lưu nguyên (không chunked trước), nên embedding của toàn bộ document dài bị "dilute" — nhiều ý không liên quan gộp chung.

**Đề xuất cải thiện:**
> (1) Chunk documents trước khi index để mỗi chunk chứa ý cụ thể, (2) Dùng real embedder để capture ngữ nghĩa, (3) Thêm metadata `topic` để filter theo chủ đề.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 8 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 9 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 7 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **80 / 100** |
