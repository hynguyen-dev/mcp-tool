# SQL Server MCP Tool

MCP Server cho phép Claude Desktop truy vấn SQL Server database một cách an toàn (chế độ read-only).

## ✨ Tính năng

- 📦 **list_databases** - Liệt kê tất cả databases trong SQL Server
- 📋 **list_tables** - Liệt kê tất cả tables trong một database
- 🔍 **sql_query** - Thực thi câu lệnh SELECT (chỉ read-only)
- 🔎 **search_text** - Tìm kiếm text (hỗ trợ Unicode: Tiếng Việt, Nhật, Trung...)

## 📋 Yêu cầu

- Python >= 3.14
- SQL Server với ODBC Driver 17
- [uv](https://github.com/astral-sh/uv) (Python package manager)

## 🚀 Cài đặt

### 1. Clone project

```bash
git clone <repo-url>
cd mcp-tool
```

### 2. Cài đặt dependencies với uv

```bash
uv sync
```

### 3. Cấu hình kết nối SQL Server

Mở file `sql_mcp.py` và chỉnh sửa thông tin kết nối:

```python
BASE_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=YOUR_SERVER_NAME;"      # Tên server của bạn
    "UID=YOUR_USERNAME;"            # Username
    "PWD=YOUR_PASSWORD;"            # Password
    "TrustServerCertificate=yes;"
)
```

## 🔧 Tích hợp với Claude Desktop

### Bước 1: Mở file cấu hình Claude Desktop

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Bước 2: Thêm cấu hình MCP Server

Thêm nội dung sau vào file `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sqlserver": {
      "command": "uv",
      "args": [
        "--directory",
        "D:/Dev/project/mcp-tool",
        "run",
        "sql_mcp.py"
      ]
    }
  }
}
```

> ⚠️ **Lưu ý**: Thay đổi đường dẫn `D:/Dev/project/mcp-tool` thành đường dẫn thực tế trên máy của bạn.

### Bước 3: Khởi động lại Claude Desktop

Đóng hoàn toàn Claude Desktop và mở lại để áp dụng cấu hình.

## 📖 Cách sử dụng

Sau khi tích hợp, bạn có thể hỏi Claude:

```
- "Liệt kê tất cả databases"
- "Cho tôi xem các tables trong database X"
- "Query: SELECT TOP 10 * FROM users"
- "Tìm kiếm từ 'nguyễn' trong tất cả databases"
```

## 🔒 Bảo mật

- Chỉ cho phép các câu lệnh **SELECT**, **WITH**, và **EXEC sp_help**
- Không hỗ trợ INSERT, UPDATE, DELETE, DROP,...
- Khuyến nghị tạo user SQL Server riêng với quyền read-only

## 📁 Cấu trúc project

```
mcp-tool/
├── sql_mcp.py        # MCP Server chính
├── pyproject.toml    # Dependencies
└── README.md         # Hướng dẫn này
```

## 🐛 Xử lý lỗi thường gặp

### Lỗi "ODBC Driver not found"

Cài đặt ODBC Driver 17 for SQL Server:
- [Download cho Windows](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Lỗi kết nối SQL Server

- Kiểm tra SQL Server đang chạy
- Kiểm tra thông tin kết nối (SERVER, UID, PWD)
- Đảm bảo SQL Server cho phép kết nối TCP/IP

### Claude Desktop không nhận MCP Server

- Kiểm tra đường dẫn trong config chính xác
- Đảm bảo `uv` đã được cài đặt và có trong PATH
- Khởi động lại Claude Desktop hoàn toàn

## 📝 License

MIT License
