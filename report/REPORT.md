# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Minh Trí
**Nhóm:** C1-C401
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:* High cosine similarity nghĩa là hai vector gần như cùng hướng, nên nội dung hoặc ý nghĩa của chúng rất giống nhau. Giá trị cosine similarity thường gần 1.

**Ví dụ HIGH similarity:**
- Sentence A: I love machine learning
- Sentence B: I really like studying machine learning.
- Tại sao tương đồng: Cả hai câu đều nói về việc thích machine learning nên embedding của chúng có hướng gần giống nhau.

**Ví dụ LOW similarity:**
- Sentence A: I love machine learning
- Sentence B: The weather is very hot today.
- Tại sao khác: Hai câu nói về chủ đề hoàn toàn khác nhau nên vector embedding của chúng không cùng hướng.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity đo độ giống nhau dựa trên hướng của vector thay vì độ dài. Với text embeddings, hướng của vector quan trọng hơn độ lớn nên cosine similarity cho kết quả phù hợp hơn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) 
> *Đáp án:* 23

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:* Bước nhảy mới: 500 − 100 = 400 → step nhỏ hơn nên số chunk sẽ tăng lên. Overlap lớn hơn giúp giữ ngữ cảnh giữa các đoạn, tránh việc thông tin quan trọng bị cắt mất ở ranh giới giữa các chunks.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Hệ thống hỗ trợ học tập và tra cứu quy trình khóa học "AI Thực Chiến" (VinUni AI20K)

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* Nhóm chọn bộ tài liệu từ Day 02 đến Day 07 vì đây là nguồn dữ liệu thực tế, có cấu trúc rõ ràng (gồm mục tiêu, timeline, tiêu chí chấm điểm và hướng dẫn kỹ thuật). Việc xây dựng RAG trên bộ dữ liệu này giúp học viên nhanh chóng tra cứu các yêu cầu bài tập (deliverables), thời hạn (deadlines) và các bước cài đặt môi trường mà không cần đọc thủ công toàn bộ các file Markdown.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Day02-AI-Product-LabsDay02-AI-Product-Labs| https://github.com/VinUni-AI20k/Day02-AI-Product-Labs| 5523| day: "02", topic: "problem_statement"|
| 2 | Day-3-Lab-Chatbot-vs-react-agent| https://github.com/VinUni-AI20k/Day-3-Lab-Chatbot-vs-react-agent| 2279| day: "03", topic: "agent_implementation"|
| 3 | Day05-AI-Product-Labs| https://github.com/VinUni-AI20k/Day-07-Lab-Data-Foundations|  10591| day: "05", topic: "product_design"|
| 4 | Day06-AI-Product-HackathonDay06-AI-Product-Hackathon| https://github.com/VinUni-AI20k/Day06-AI-Product-Hackathon| 14954| day: "06", topic: "hackathon"|
| 5 | Day-07-Lab-Data-Foundations| https://github.com/VinUni-AI20k/Day05-AI-Product-Labs| 6628| day: "07", topic: "embedding_rag"|


### Metadata Schema

| Trường metadata | Kiểu   | Ví dụ giá trị    | Tại sao hữu ích cho retrieval?                     |
| --------------- | ------ | ---------------- | -------------------------------------------------- |
| type            | string | lecture / lab    | Lọc theo loại nội dung (bài giảng lý thuyết hay thực hành) |
| topic           | string | agents, data     | Thu hẹp phạm vi theo chủ đề kỹ thuật               |
| day             | integer| 7                | Tìm kiếm thông tin theo lộ trình thời gian của khóa học |
| priority        | string | high             | Ưu tiên các hướng dẫn quan trọng khi trả về kết quả |
| source          | string | vinuni           | Xác nhận nguồn tin cậy của bài|

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| day02.md | FixedSizeChunker (`fixed_size`) | 37 | 198.0 |No|
| day02.md | SentenceChunker (`by_sentences`) | 7 | 787.5714285714286 |Partial|
| day02.md | RecursiveChunker (`recursive`) | 45 | 121.08888888888889 |Yes|
| day03.md | FixedSizeChunker (`fixed_size`) | 16 | 192.875 |No|
| day03.md | SentenceChunker (`by_sentences`) | 9 | 257.3333333333333 |Partial|
| day03.md | RecursiveChunker (`recursive`) | 17 | 135.8235294117647 |Yes|

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?* RecursiveChunker chia văn bản theo thứ tự ưu tiên của các dấu phân cách như \n\n, \n, . , khoảng trắng và cuối cùng là cắt theo độ dài cố định nếu cần. Nếu một đoạn sau khi tách vẫn lớn hơn chunk_size, thuật toán sẽ tiếp tục chia nhỏ đoạn đó bằng dấu phân cách tiếp theo. Quá trình này diễn ra đệ quy cho đến khi tất cả các chunk đều nhỏ hơn hoặc bằng kích thước tối đa. Nhờ vậy, chunk thường giữ được cấu trúc tự nhiên của văn bản như đoạn văn hoặc câu.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?* Tài liệu trong domain của nhóm (ví dụ: markdown hoặc tài liệu kỹ thuật) thường có cấu trúc rõ ràng theo đoạn và câu. RecursiveChunker tận dụng các dấu phân cách tự nhiên này để giữ nguyên ngữ cảnh của nội dung. Điều này giúp các chunk mang ý nghĩa đầy đủ hơn và cải thiện chất lượng truy xuất trong hệ thống RAG.

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| day02.md | best baseline (FixedSize) | 37 | 198.0 | Medium |
| day02.md| **của tôi (recursive)** | 45 | 121.09 | High |
| day03.md| best baseline (FixedSize) | 16 | 192.88 | Medium |
| day03.md| **của tôi (recursive)** | 17 | 135.82 | High |


### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi |RecursiveChunker |9.5/10|Giữ semantic context tốt, chunk nhỏ hợp lý (~120–135 tokens), cải thiện độ chính xác retrieval |Chunk count nhiều hơn → index lớn hơn |
| Phương |FixedSizeChunker |9/10|Đơn giản, tốc độ xử lý nhanh, chunk size ổn định |Dễ cắt giữa câu hoặc ý → context bị vỡ |
| Thành |SentenceChunker |8.5/10|Giữ câu hoàn chỉnh, ít phá vỡ ngữ nghĩa |Chunk dài không đều, đôi khi chứa nhiều ý khác nhau |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:* Recursive chunking là strategy phù hợp nhất cho domain này vì nó chia tài liệu theo cấu trúc ngữ nghĩa (paragraph → sentence → token), giúp giữ được ngữ cảnh của nội dung. Điều này làm cho các đoạn được truy xuất có liên quan hơn khi dùng trong hệ thống RAG. So với fixed-size hoặc sentence chunking, recursive chunking giảm việc cắt giữa ý và cải thiện chất lượng retrieval.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?* Sentence detection được thực hiện bằng regex (?<=[.!?])\s+, tách văn bản sau các dấu kết thúc câu như ., !, hoặc ?. Sau khi tách, các câu được nhóm lại thành từng chunk với tối đa max_sentences_per_chunk câu. Hàm cũng loại bỏ khoảng trắng thừa và xử lý edge case khi input rỗng bằng cách trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?* Thuật toán sử dụng chiến lược chia văn bản theo thứ tự ưu tiên của các separator như \n\n, \n, . , và khoảng trắng. Nếu một đoạn vẫn lớn hơn chunk_size, hàm _split sẽ tiếp tục chia đệ quy với separator tiếp theo cho đến khi đạt kích thước phù hợp. Base case là khi đoạn văn bản đã nhỏ hơn chunk_size hoặc khi không còn separator nào, lúc đó văn bản sẽ được cắt cứng theo kích thước tối đa.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?* Khi thêm tài liệu, mỗi document được chuyển thành embedding bằng hàm embedding và lưu kèm nội dung cùng metadata. Khi tìm kiếm, query cũng được embed thành vector và độ tương đồng giữa query và từng document được tính bằng dot product (hoặc cosine similarity). Các kết quả sau đó được sắp xếp theo score giảm dần và trả về top_k document liên quan nhất.

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?* search_with_filter thực hiện lọc metadata trước khi chạy similarity search để giảm số lượng candidate cần so sánh. Hàm delete_document loại bỏ tất cả record có id trùng với document cần xóa khỏi store, sau đó trả về True nếu có dữ liệu bị xóa hoặc False nếu không tìm thấy document.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?* Agent sử dụng mô hình Retrieval-Augmented Generation (RAG) bằng cách truy xuất các chunk liên quan từ vector store trước. Các chunk này được ghép lại thành phần context và chèn vào prompt cùng với câu hỏi của người dùng. Prompt hoàn chỉnh sau đó được gửi tới LLM để sinh ra câu trả lời dựa trên thông tin trong context.

### Test Results

```
# Paste output of: pytest tests/ -v
PS D:\Python\Day07\Day-07-Lab-Data-Foundations> pytest tests/ -v
============================================================ test session starts =============================================================
platform win32 -- Python 3.13.12, pytest-9.0.3, pluggy-1.6.0 -- D:\Python\Day07\Day-07-Lab-Data-Foundations\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Python\Day07\Day-07-Lab-Data-Foundations
collected 42 items                                                                                                                            

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                   [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                            [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                     [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                      [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                           [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                           [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                 [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                  [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                  [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                  [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                             [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                         [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                   [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                          [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                              [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                        [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                              [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                  [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                    [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                      [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                            [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                 [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                   [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                       [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                    [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                             [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                            [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                       [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                   [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                              [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                  [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                        [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                  [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                               [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                             [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                            [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                           [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                    [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                          [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                              [100%]

============================================================= 42 passed in 0.10s =============================================================
```

**Số tests pass:** 42/42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Mục tiêu của Lab Ngày 7 là tìm hiểu về Vector Store" | "Học cách triển khai RAG pattern trong Lab 7" | Cao | -0.0398 | Sai |
| 2 | "Cách cài đặt Local Embedder" | "Sử dụng sentence-transformers để chạy embedding" | Cao | -0.0909 | Sai |
| 3 | "RecursiveChunker chia nhỏ văn bản đệ quy" | "Chiến lược chunking dựa trên câu" | Trung bình | -0.0355 | Đúng |
| 4 | "Hệ thống RAG giúp chatbot tra cứu tài liệu" | "Thời tiết hôm nay có nắng nhẹ" | Thấp | -0.0926 | Đúng |
| 5 | "Nộp bài vào thư mục report" | "Hoàn thành các TODO trong src package" | Trung bình | 0.1969 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:* Kết quả bất ngờ nhất là pair 2, vì hai câu đều liên quan đến việc thiết lập embedding nhưng mô hình vẫn cho độ tương đồng thấp. Điều này cho thấy embeddings không chỉ dựa vào chủ đề chung mà còn phụ thuộc vào cách diễn đạt và ngữ cảnh cụ thể của câu. Các mô hình embedding đôi khi khó nhận ra sự liên quan nếu các thuật ngữ hoặc cấu trúc câu khác nhau.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Cách tính điểm cho bài tập UX Ngày 5 là gì? | Dựa trên tiêu chí trải nghiệm người dùng và tính khả thi (chi tiết trong day05.md). |
| 2 | Các giai đoạn chính của Lab Ngày 7 gồm những gì? | Gồm 2 Phase: Cá nhân (implement src) và Nhóm (benchmark strategy). |
| 3 | Deadline nộp SPEC draft là lúc mấy giờ? | Thường được quy định vào cuối ngày hoặc theo timeline trong day05.md. |
| 4 | Sự khác biệt giữa Mock prototype và Working prototype là gì? | Mock là bản mô phỏng giao diện, Working là bản có chức năng thực tế (day06.md). |
| 5 | Cấu trúc thư mục của Phase 3 yêu cầu gì? | Yêu cầu các folder src, tests và notebook rõ ràng (day03.md). |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Cách tính điểm cho bài tập UX Ngày 5 là gì? | # Ngày 5 — Thiết kế sản phẩm AI cho sự không chắc chắn... | 0.0469 | Đúng | [MOCK LLM] Dựa trên tài liệu Lab: "# Ngày 5 — Thiế... |
| 2 | Các giai đoạn chính của Lab Ngày 7 gồm những gì? | # Lab 3: Chatbot vs ReAct Agent (Industry Edition) | -0.0387 | Sai | [MOCK LLM] Dựa trên tài liệu Lab: "# Lab 3: Chatbo... |
| 3 | Deadline nộp SPEC draft là lúc mấy giờ? | # Ngày 6 — Hackathon: SPEC → Prototype → Demo... | 0.1817 | Đúng | [MOCK LLM] Dựa trên tài liệu Lab: "# Ngày 6 — Hack... |
| 4 | Sự khác biệt giữa Mock prototype và Working prototype là gì? | # Ngày 2 — Tìm Đúng Bài Toán — Updated for v2 Metrics... | 0.1667 | Đúng | [MOCK LLM] Dựa trên tài liệu Lab: "# Ngày 2 — Tìm ... |
| 5 | Cấu trúc thư mục của Phase 3 yêu cầu gì? | ### 3. Directory Structure\n- `src/tools/`: Extension... | 0.0293 | Đúng | [MOCK LLM] Dựa trên tài liệu Lab: "### 3. Directo... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 4 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:* Tôi học được rằng việc sử dụng các chiến lược chunking khác nhau có thể ảnh hưởng đáng kể đến chất lượng truy xuất trong hệ thống RAG. Ví dụ, FixedSizeChunker tuy đơn giản nhưng đôi khi làm mất ngữ cảnh nếu cắt giữa câu. So sánh các chiến lược giúp nhóm hiểu rõ hơn khi nào nên ưu tiên semantic context.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:* Một số nhóm đã thử nghiệm nhiều cách tổ chức metadata và filtering để cải thiện kết quả retrieval. Điều này giúp hệ thống không chỉ dựa vào similarity mà còn dựa vào thông tin ngữ cảnh như topic hoặc loại tài liệu. Cách tiếp cận này giúp kết quả tìm kiếm chính xác và có kiểm soát hơn.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:* Nếu làm lại, tôi sẽ chuẩn hóa metadata rõ ràng hơn ngay từ đầu để hỗ trợ filtering tốt hơn trong vector store. Ngoài ra, tôi cũng muốn thử thêm hybrid retrieval kết hợp giữa semantic search và keyword search để cải thiện độ chính xác khi truy xuất thông tin.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **90 / 100** |
