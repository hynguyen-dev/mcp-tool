import os
import pyodbc
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sqlserver")

# ===============================
# 🔐 Base connection (no database)
# ===============================
BASE_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={os.getenv('SQL_SERVER', 'GIGABYTE')};"
    f"UID={os.getenv('SQL_USER', 'AI_READER')};"
    f"PWD={os.getenv('SQL_PASSWORD', 'mcp@ngtuonghy')};"
    "TrustServerCertificate=yes;"
)

def get_conn(db: str):
    return pyodbc.connect(BASE_CONN + f"DATABASE={db};")

# ===============================
# 🔒 Read-only protection
# ===============================
def is_safe(query: str):
    q = query.strip().lower()
    return (
        q.startswith("select")
        or q.startswith("with")
        or q.startswith("exec sp_help")
    )

# ===============================
# 📦 List all databases
# ===============================
@mcp.tool()
def list_databases():
    """
    List all databases in this SQL Server instance.
    """
    conn = pyodbc.connect(BASE_CONN + "DATABASE=master;")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases ORDER BY name")
    return [r[0] for r in cursor.fetchall()]

# ===============================
# 📋 List tables in a database
# ===============================
@mcp.tool()
def list_tables(database: str):
    """
    List all tables in a given database.
    """
    conn = get_conn(database)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    return [{"schema": r[0], "table": r[1]} for r in cursor.fetchall()]

# ===============================
# 🔍 Query a specific database
# ===============================
@mcp.tool()
def sql_query(database: str, query: str):
    """
    Run a read-only SQL query on a specific database.
    Only SELECT queries are allowed.
    """
    if not is_safe(query):
        return {"error": "Read-only mode. Only SELECT allowed."}

    conn = get_conn(database)
    cursor = conn.cursor()
    cursor.execute(query)

    cols = [c[0] for c in cursor.description]
    rows = cursor.fetchall()

    return {
        "database": database,
        "columns": cols,
        "rows": [list(r) for r in rows]
    }

# ===============================
# 🔎 Search text across databases
# ===============================
@mcp.tool()
def search_text(text: str, databases: list[str], max_rows: int = 20):
    """
    Search for Unicode text (Japanese, Chinese, etc) across all tables & columns
    in multiple databases.
    """
    results = []

    for db in databases:
        conn = get_conn(db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE DATA_TYPE IN ('varchar','nvarchar','char','nchar','text','ntext')
        """)
        columns = cursor.fetchall()

        for schema, table, col in columns:
            try:
                sql = f"""
                SELECT TOP {max_rows}
                    '{db}' AS database_name,
                    '{schema}.{table}' AS table_name,
                    '{col}' AS column_name,
                    CAST({col} AS NVARCHAR(MAX)) AS value
                FROM {schema}.{table}
                WHERE CAST({col} AS NVARCHAR(MAX)) LIKE ?
                """
                cursor.execute(sql, f"%{text}%")

                for r in cursor.fetchall():
                    results.append({
                        "database": r[0],
                        "table": r[1],
                        "column": r[2],
                        "value": r[3]
                    })
            except:
                pass

    return results

# ===============================
# 🚀 Start MCP for Claude
# ===============================
if __name__ == "__main__":
    mcp.run(transport="stdio")
