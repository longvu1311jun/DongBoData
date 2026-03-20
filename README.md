# 📦 DataSync Pro

Ứng dụng GUI Python đồng bộ dữ liệu **Products**, **Orders**, **Customers** từ API.

## Cấu trúc dự án

```
py/
├── main.py        # Entry point - chạy từ đây
├── gui.py         # Giao diện chính (Tkinter)
├── config.py      # Cấu hình app
└── README.md      # File này
```

## Cách sử dụng

### 1. Cài đặt
```bash
pip install requests
```
Hoặc chạy trực tiếp `main.py` — sẽ tự cài nếu thiếu.

### 2. Chạy
```bash
python main.py
```

### 3. Hướng dẫn

1. **Nhập Base URL** — API endpoint gốc của bạn (ví dụ: `https://api.yourdomain.com`)
2. **Nhập Headers** — Thêm token Authorization hoặc header tùy chọn (JSON)
3. **Chọn dữ liệu** — Check vào Products / Orders / Customers cần sync
4. **Chọn chế độ** — Full Sync hoặc Incremental
5. **Bấm "BẮT ĐẦU ĐỒNG BỘ"** — Tool sẽ gọi API và tải data

## Cấu trúc API mặc định

| Loại dữ liệu | Endpoint        |
|---------------|-----------------|
| Products      | `/api/products` |
| Orders        | `/api/orders`   |
| Customers     | `/api/customers`|

> Có thể tùy chỉnh endpoint trong `config.py`

## Tính năng

- ✅ Giao diện dark-mode hiện đại
- ✅ Đồng bộ song song nhiều loại dữ liệu
- ✅ Progress bar theo từng loại
- ✅ Nhật ký chi tiết (log)
- ✅ Export log ra file
- ✅ Timeout & error handling
- ✅ Hỗ trợ custom headers (Authorization, etc.)
- ✅ Chế độ Full / Incremental sync
- ✅ Lưu cấu hình

## Mở rộng

Sau khi bạn cung cấp API, tôi sẽ mở rộng để:
1. Lưu data vào database (SQLite / PostgreSQL / MySQL)
2. Tự động schedule sync định kỳ
3. Validate & transform data
4. Dashboard thống kê
5. Backup & restore

