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

### 3. Cấu hình biến môi trường

Kết nối SQL Server được cấu hình qua biến môi trường:

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `SQL_SERVER` | Tên server SQL | `localhost` |
| `SQL_USER` | Username | `sa` |
| `SQL_PASSWORD` | Password | (trống) |

Có thể cấu hình trực tiếp trong `claude_desktop_config.json` (xem bước tiếp theo).

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
      ],
      "env": {
        "SQL_SERVER": "GIGABYTE",
        "SQL_USER": "AI_READER",
        "SQL_PASSWORD": "mcp@ngtuonghy"
      }
    }
  }
}
```

> ⚠️ **Lưu ý**: 
> - Thay đổi đường dẫn `D:/Dev/project/mcp-tool` thành đường dẫn thực tế trên máy của bạn.
> - Cập nhật `SQL_SERVER`, `SQL_USER`, `SQL_PASSWORD` với thông tin kết nối của bạn.

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

### Tạo user SQL Server với quyền read-only

Chạy các lệnh SQL sau trong SQL Server Management Studio (SSMS) với quyền admin:

```sql
-- 1. Tạo Login ở cấp Server
CREATE LOGIN AI_READER WITH PASSWORD = 'your_secure_password';

-- 2. Cấp quyền xem tất cả databases
GRANT VIEW ANY DATABASE TO AI_READER;

-- 3. Tạo User và cấp quyền đọc cho từng database
-- Thay 'YourDatabase' bằng tên database thực tế
-- Lặp lại cho mỗi database bạn muốn cho phép truy cập

USE [YourDatabase];
GO
CREATE USER AI_READER FOR LOGIN AI_READER;
GO
-- Cấp quyền đọc tất cả tables
ALTER ROLE db_datareader ADD MEMBER AI_READER;
GO
-- Cấp quyền xem definition (để xem cấu trúc tables, views, stored procedures)
GRANT VIEW DEFINITION TO AI_READER;
GO
```

**Script tự động cấp quyền cho TẤT CẢ databases:**

```sql
-- =============================================
-- QUAN TRỌNG: Chạy script này trong database master
-- =============================================
USE master;
GO

-- =============================================
-- BƯỚC 1: Tạo Login (chạy 1 lần duy nhất)
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'AI_READER')
BEGIN
    CREATE LOGIN AI_READER WITH PASSWORD = 'mcp@ngtuonghy';
    PRINT 'Login AI_READER created successfully.';
END
ELSE
    PRINT 'Login AI_READER already exists.';
GO

-- Cấp quyền xem tất cả databases
GRANT VIEW ANY DATABASE TO AI_READER;
GO

-- =============================================
-- BƯỚC 2: Cấp quyền đọc cho tất cả databases
-- =============================================
DECLARE @dbname NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);

DECLARE db_cursor CURSOR FOR
SELECT name FROM sys.databases
WHERE state = 0  -- Online databases only
  AND name NOT IN ('tempdb')  -- Bỏ qua tempdb
  AND database_id > 4;  -- Bỏ qua system databases (master, model, msdb, tempdb)

OPEN db_cursor;
FETCH NEXT FROM db_cursor INTO @dbname;

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = '
    USE [' + @dbname + '];
    IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = ''AI_READER'')
    BEGIN
        CREATE USER AI_READER FOR LOGIN AI_READER;
    END
    ALTER ROLE db_datareader ADD MEMBER AI_READER;
    GRANT VIEW DEFINITION TO AI_READER;
    ';
    
    BEGIN TRY
        EXEC sp_executesql @sql;
        PRINT 'Granted access to: ' + @dbname;
    END TRY
    BEGIN CATCH
        PRINT 'Error on database: ' + @dbname + ' - ' + ERROR_MESSAGE();
    END CATCH
    
    FETCH NEXT FROM db_cursor INTO @dbname;
END

CLOSE db_cursor;
DEALLOCATE db_cursor;

PRINT 'Done! User AI_READER has read access to all user databases.';
```

> 💡 **Tip**: Thay `AI_READER` và `your_secure_password` bằng username/password bạn muốn sử dụng, sau đó cập nhật trong file `sql_mcp.py`.

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
