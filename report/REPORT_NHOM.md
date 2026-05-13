# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm AI Foundations
**Thành viên:** Trịnh Kế Tiến (2A202600500)

---

## Phân Công Công Việc

| Phase | Công việc | Phụ trách |
|-------|----------|----------|
| Phase 1 — Cá nhân | Implement src package (chunking, store, agent) | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Chọn domain & thu thập tài liệu | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Thiết kế metadata schema | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Viết 5 benchmark queries + gold answers | Trịnh Kế Tiến |
| Phase 2 — Nhóm | Chạy benchmark & phân tích kết quả | Trịnh Kế Tiến |
| Phase 2 — Nhóm | So sánh strategy & failure analysis | Trịnh Kế Tiến |

---

## 1. Document Selection (10 điểm)

### Domain & Lý Do Chọn

**Domain:** AI Engineering — Knowledge Assistant & RAG Systems

**Tại sao chọn domain này?**
> Chọn domain AI Engineering vì trực tiếp liên quan đến nội dung lab — embedding, vector store, và RAG. Bộ tài liệu bao gồm cả tiếng Anh và tiếng Việt, cho phép kiểm tra retrieval đa ngôn ngữ. Các tài liệu đa dạng từ coding guides, system design, đến support playbook.

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
| category | string | "technical" / "general" | Phân loại tài liệu kỹ thuật vs tổng hợp, filter khi user hỏi chuyên sâu |
| lang | string | "en" / "vi" | Lọc theo ngôn ngữ, tránh trả về tài liệu sai ngôn ngữ |

---

## 2. Chunking Strategy (15 điểm)

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

### Strategy Đã Chọn

**Loại:** RecursiveChunker (tuned: chunk_size=300)

**Mô tả cách hoạt động:**
> RecursiveChunker thử tách text bằng separator theo thứ tự ưu tiên: `\n\n` → `\n` → `. ` → ` ` → `""`. Khi gặp separator có thể tách, nó chia thành các phần nhỏ. Nếu phần nào vẫn lớn hơn chunk_size, đệ quy xuống separator tiếp theo. Cuối cùng các phần nhỏ liền kề merge lại nếu tổng ≤ chunk_size.

**Tại sao chọn strategy này cho domain?**
> Domain AI Engineering có tài liệu markdown với cấu trúc rõ ràng: heading, paragraph, bullet points. RecursiveChunker khai thác cấu trúc này bằng cách ưu tiên tách theo paragraph boundary trước.

### So Sánh Giữa Các Strategy (tự thử nghiệm)

> *Nhóm chỉ có 1 thành viên, nên tự thử cả 3 strategy trên cùng bộ tài liệu để so sánh.*

| Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|----------|----------------------|-----------|----------|
| RecursiveChunker (300) | 7/10 | Giữ cấu trúc paragraph, linh hoạt | Chunk có thể quá nhỏ |
| SentenceChunker (3) | 6/10 | Chunk đọc tự nhiên | Chunk dài, pha trộn ý |
| FixedSizeChunker (200) | 5/10 | Đơn giản, dự đoán được | Cắt giữa câu |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> RecursiveChunker phù hợp nhất vì tài liệu có cấu trúc markdown rõ ràng. Nó tôn trọng ranh giới paragraph và heading, giữ ý trọn vẹn.

### So Sánh: Strategy Đã Chọn vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|-------------------|
| chunking_experiment_report | best baseline (SentenceChunker) | 5 | 395.6 | Tốt nhưng chunk dài |
| chunking_experiment_report | **RecursiveChunker (của tôi)** | 18 | 108.44 | Chunk ngắn gọn, đúng section |

---

## 3. Benchmark Queries & Gold Answers (10 điểm)

| # | Query | Gold Answer | Chunk nào chứa thông tin? |
|---|-------|-------------|--------------------------|
| 1 | What are the main use cases of Python in production? | Python is used for APIs, data pipelines, internal tools, and model-serving layers | python_intro (paragraph 2) |
| 2 | How does a vector search pipeline work? | Chunk documents, embed chunks, store vectors with metadata, embed query and rank by similarity | vector_store_notes (Typical Workflow) |
| 3 | What chunking strategy performed best in the experiment? | Recursive chunking offered the best balance in the experiment | chunking_experiment_report (Recursive Chunking + Conclusion) |
| 4 | How should customer support content be written for retrieval? | Authors should specify exact page, button, or log source instead of vague statements | customer_support_playbook (paragraph 2) |
| 5 | What is the role of metadata in retrieval systems? | Metadata helps filter search space by department, language, date to improve precision | vector_store_notes (Metadata Matters) + vi_retrieval_notes |

### Metadata Filter Test

| Query | Mode | Kết quả | Nhận xét |
|-------|------|---------|----------|
| "retrieval quality" | filter lang=vi | 1 result (vi_retrieval_notes, score=-0.076) | Chỉ trả về tài liệu tiếng Việt đúng |
| "retrieval quality" | unfiltered | 3 results (top: customer_support, score=0.061) | Kết quả pha trộn, không chính xác |

> Metadata filtering giúp tăng precision khi biết rõ scope cần tìm.

---

## 4. What I Learned — Demo (5 điểm)

**Điều hay nhất học được khi thử nghiệm 3 strategies:**
> SentenceChunker cho FAQ ngắn gọn tốt hơn RecursiveChunker. Strategy phức tạp không luôn tốt hơn — phụ thuộc vào cấu trúc tài liệu.

**Bài học từ quá trình thực nghiệm:**
> Metadata filter theo ngôn ngữ (lang=vi) giúp lọc chính xác khi embedder rank sai. Trong production, filter theo department/language/date rất quan trọng.

**Nếu làm lại, thay đổi gì trong data strategy?**
> (1) Real embedder thay mock, (2) metadata phong phú hơn (date, author, difficulty), (3) chunk trước khi index.

