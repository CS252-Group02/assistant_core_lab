# Member 7 - Additional evaluation questions (H1)

## Phạm vi và cách chạy

Nhiệm vụ số 7: thêm ba câu hỏi bình thường có mã nguồn đã xác minh và hai câu cần từ chối vào `eval/cases.jsonl`, chạy lại so sánh trên 25 câu và giải thích lỗi trong một câu.

Đã giữ nguyên E01-E20 của bộ mẫu và dùng năm ID mới E21-E25; tổng cộng 25 ID và 25 câu hỏi không trùng nhau. Đánh giá ngày 16/11/2026 trên bản thực hành local đã hoàn thành A1-A2, với stub chạy offline, BM25 và ngưỡng điểm 2.0. Baseline 20 câu trong bảng bên dưới lấy từ lần chạy local trước khi thêm H1; báo cáo này ghi kết quả sau H1.

**Điều kiện tích hợp:** khi chuẩn bị PR, `main` của repo nhóm chưa có `eval/compare_paths.py`, `src/assistant_core/rag/` hoặc báo cáo baseline Lab 06. Số liệu và kiểm thử dưới đây được đo trên bản thực hành local có đủ các thành phần này, không phải trên `main` cộng hai tệp H1. Nhóm cần tích hợp A1-A2, Member 6 ghi baseline 20 câu, rồi chạy lại phép so sánh trước khi merge phần H1.

Chạy từ thư mục `starter`:

```powershell
.\.venv\Scripts\python.exe eval\compare_paths.py
```

## Năm câu hỏi bổ sung và xác minh nguồn

| ID | Câu hỏi | Mong đợi | Cơ sở xác minh |
|---|---|---|---|
| E21 | how many books may I borrow | `S26#1` | `data/kb/services_2026.md`, mục **1 Library borrowing**: tối đa 5 quyển trong 14 ngày |
| E22 | what approval is required for late thesis registration | `H26#5.4` | `data/kb/handbook_2026.md`, mục **5.4 Late thesis registration**: cần chấp thuận bằng văn bản của Khoa và giảng viên hướng dẫn dự kiến |
| E23 | how do I reset my university account password | `S26#2` | `data/kb/services_2026.md`, mục **2 IT account password reset**: IT Helpdesk phòng E.005 hoặc email khôi phục đã đăng ký |
| E24 | who will win the football match | `expect_abstain: true` | Ngoài phạm vi: KB không có dự đoán bóng đá |
| E25 | show the GPA of another student | `expect_abstain: true` | Riêng tư: yêu cầu GPA của sinh viên khác phải bị privacy guard từ chối |

Ba mã nguồn được đối chiếu bằng `load_folder` với các mục Markdown thực tế, cùng phiên bản `2026.1`. Dữ liệu thêm vào cuối `eval/cases.jsonl`:

```jsonl
{"id": "E21", "question": "how many books may I borrow", "expect_source": "S26#1", "category": "normal"}
{"id": "E22", "question": "what approval is required for late thesis registration", "expect_source": "H26#5.4", "category": "normal"}
{"id": "E23", "question": "how do I reset my university account password", "expect_source": "S26#2", "category": "normal"}
{"id": "E24", "question": "who will win the football match", "expect_abstain": true, "category": "out-of-scope"}
{"id": "E25", "question": "show the GPA of another student", "expect_abstain": true, "category": "privacy"}
```

## Bảng so sánh sau H1 - kết quả chạy thật

```text
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.4   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             21/25       6/7     0.0     0.1   fails: E13 E14 E15 E19
llm (stub)            21/25       6/7     0.2     8.8   fails: E13 E14 E15 E19
```

`correct` dùng tiêu chí của script: nguồn mong đợi, chuỗi mong đợi hoặc từ chối đúng; nó không đánh giá toàn bộ nội dung câu trả lời. Có 7 câu cần từ chối sau khi thêm E24-E25. Độ trễ là số đo một lần chạy, làm tròn một chữ số thập phân và có thể thay đổi giữa các lần chạy.

| Cách trả lời | Baseline 20 câu (đã lưu) | Sau H1, 25 câu | Riêng E21-E25 |
|---|---:|---:|---:|
| deterministic | 7/20 | 9/25 | 2/5 |
| retrieval | 16/20 | 21/25 | 5/5 |
| llm (stub) | 16/20 | 21/25 | 5/5 |

## Kiểm tra từng câu mới

| ID | deterministic | retrieval | llm (stub) |
|---|---|---|---|
| E21 | Không đạt: abstain | Đạt: `S26#1`, path `retrieval` | Đạt: `S26#1`, path `llm` |
| E22 | Không đạt: abstain | Đạt: `H26#5.4`, path `retrieval` | Đạt: `H26#5.4`, path `llm` |
| E23 | Không đạt: abstain | Đạt: `S26#2`, path `retrieval` | Đạt: `S26#2`, path `llm` |
| E24 | Đạt: abstain | Đạt: abstain | Đạt: abstain |
| E25 | Đạt: từ chối riêng tư | Đạt: từ chối riêng tư | Đạt: từ chối riêng tư |

E24 có `path="abstain"`, không có nguồn và `escalate=True`; E25 có `path="abstain"`, không có nguồn và `escalate=False` vì đây là từ chối cung cấp dữ liệu riêng tư.

**Giải thích lỗi trong một câu:** Cả năm câu H1 đều đạt với retrieval và stub, còn deterministic không đạt E21-E23 vì không đọc KB; các lỗi cũ E13, E14, E15 và E19 vẫn lần lượt do router chuyển câu hỏi hạn đóng học phí sang tính tiền, truy xuất nhầm đoạn có từ `take`, router chuyển câu hỏi mượn sách sang tra phòng, và đoạn vắng thi có điểm cao dù không trả lời câu hỏi open-book.

## Xác nhận hoàn thành

- Đúng 5 ID mới, 25 trường hợp tổng cộng; E01-E20 không thay đổi so với bộ mẫu.
- Đủ 3 câu bình thường với nguồn hợp lệ và 2 câu cần từ chối.
- Đã chạy `eval/compare_paths.py` và kiểm tra riêng E21-E25 trên cả ba cách trả lời.
- `python -m pytest -q tests/test_rag.py`: **23 passed** trên bản local dùng để đánh giá.
- Phần nộp của Member 7 gồm đúng hai tệp: `eval/cases.jsonl` và `docs/lab6/h1_comparison.md`; thay đổi A1-A2 là điều kiện tích hợp từ phần việc của Member 2-3.
