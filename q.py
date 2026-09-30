r"""
Your SQL practice tool. Runs queries against practice.db and prints the result
as a table.

Three ways to use it:

  1. One query straight from the command line:
       py q.py "SELECT * FROM employees LIMIT 5"

  2. Run a .sql file (can hold several statements separated by ;):
       py q.py scratch.sql

  3. Interactive mode - just launch it with no arguments:
       py q.py
     Then type SQL and press Enter. End a statement with ; to run it.
     Type  \schema  to see all tables and columns,  \tables  for table names,
     and  \q  (or Ctrl+C) to quit.
"""
import os
import sys
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "practice.db")
MAX_CELL = 40  # long text values are trimmed to this width when printed


def render(cursor):
    rows = cursor.fetchall()
    if cursor.description is None:
        print("(statement ran, no rows returned)")
        return
    headers = [d[0] for d in cursor.description]

    def cell(v):
        if v is None:
            return "NULL"
        s = str(v)
        return s if len(s) <= MAX_CELL else s[: MAX_CELL - 1] + "…"

    table = [headers] + [[cell(v) for v in r] for r in rows]
    widths = [max(len(row[i]) for row in table) for i in range(len(headers))]

    def line(row):
        return " | ".join(val.ljust(widths[i]) for i, val in enumerate(row))

    print(line(headers))
    print("-+-".join("-" * w for w in widths))
    for r in table[1:]:
        print(line(r))
    print(f"\n{len(rows)} row(s)")


def run_sql(conn, sql):
    sql = sql.strip()
    if not sql:
        return
    try:
        # Split on ';' so a file / paste with several statements works.
        statements = [s for s in sql.split(";") if s.strip()]
        for i, stmt in enumerate(statements):
            if len(statements) > 1:
                print(f"--- statement {i + 1} ---")
            cur = conn.execute(stmt)
            render(cur)
            conn.commit()
            if len(statements) > 1:
                print()
    except sqlite3.Error as e:
        print(f"SQL ERROR: {e}")


def show_schema(conn):
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    for t in tables:
        print(f"\n{t}")
        for cid, name, ctype, notnull, dflt, pk in conn.execute(f"PRAGMA table_info({t})"):
            tags = []
            if pk:
                tags.append("PRIMARY KEY")
            if notnull:
                tags.append("NOT NULL")
            tag = ("  " + ", ".join(tags)) if tags else ""
            print(f"  {name:16} {ctype}{tag}")


def interactive(conn):
    print("Interactive SQL.  End a statement with ;   Commands: \\schema  \\tables  \\q")
    buf = ""
    while True:
        try:
            prompt = "sql> " if not buf else "...> "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        s = line.strip()
        if not buf and s in (r"\q", r"\quit", "exit", "quit"):
            return
        if not buf and s in (r"\schema", r"\d"):
            show_schema(conn)
            continue
        if not buf and s in (r"\tables", r"\dt"):
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
                print(" ", r[0])
            continue
        buf += line + "\n"
        if ";" in line:
            run_sql(conn, buf)
            buf = ""


def main():
    if not os.path.exists(DB_PATH):
        print("practice.db not found. Build it first:  py setup_db.py")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg is None:
        interactive(conn)
    elif arg in ("--schema", "-s", r"\schema"):
        show_schema(conn)
    elif os.path.isfile(arg):
        with open(arg, "r", encoding="utf-8") as f:
            run_sql(conn, f.read())
    else:
        run_sql(conn, " ".join(sys.argv[1:]))

    conn.close()


if __name__ == "__main__":
    main()
