r"""
SQL TUTOR - an interactive, self-grading SQL course.

    py tutor.py              start / resume where you left off
    py tutor.py --status     show your progress and scores
    py tutor.py --reset      wipe progress and start over
    py tutor.py --lesson 3   jump straight to a specific lesson
    py tutor.py --selftest   (for maintenance) run every reference answer

While answering an SQL question you can type these commands instead of SQL:
    :hint       show a hint
    :schema     show all tables and columns
    :skip       give up on this question (scores 0)
    :solution   reveal a correct answer (scores 0)
    :quit       save and exit

How grading works:
  - Your query is run and its result compared to a reference answer.
  - SQL question: correct on 1st try = full marks, 2nd = 0.7, 3rd = 0.4, else 0.
  - Multiple-choice: right = 1, wrong = 0 (explanation always shown).
  - Lesson passed at 80% average. Below that, the missed questions are re-drilled.
"""
import argparse
import datetime as _dt
import json
import os
import re
import sqlite3
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "practice.db")
PROGRESS_PATH = os.path.join(HERE, "progress.json")
PASS_MARK = 0.8
ATTEMPT_WEIGHT = {1: 1.0, 2: 0.7, 3: 0.4}

LESSONS = {
    1: "SELECT, FROM, columns, aliases, expressions",
    2: "WHERE - filtering rows",
    3: "ORDER BY, LIMIT, DISTINCT",
    4: "NULL - IS NULL, IS NOT NULL, COALESCE",
}
MAX_LESSON = max(LESSONS)

# ---------------------------------------------------------------------------
# Question bank
#   type "sql":  prompt, solution, optional ordered / check_columns / hint / teach
#   type "mcq":  prompt, choices (list), answer (letter), teach
# ---------------------------------------------------------------------------
QUESTIONS = [
    # ---- Lesson 1 --------------------------------------------------------
    dict(id="L1Q1", lesson=1, type="mcq",
         prompt="In  SELECT last_name, salary FROM employees;  which clause chooses the TABLE?",
         choices=["SELECT", "FROM", "the semicolon", "last_name"],
         answer="b",
         teach="FROM names the table the rows come from. SELECT is the list of "
               "columns/expressions to return. The semicolon just ends the statement."),
    dict(id="L1Q2", lesson=1, type="sql",
         prompt="Show the project_name and budget of every project.",
         solution="SELECT project_name, budget FROM projects;",
         hint="Two column names separated by a comma, then FROM projects.",
         teach="Column list + FROM. The order you name columns in SELECT is the order "
               "they appear in the result."),
    dict(id="L1Q3", lesson=1, type="sql",
         prompt="Show every column of the departments table.",
         solution="SELECT * FROM departments;",
         hint="There is a one-character shortcut that means 'all columns'.",
         teach="SELECT * returns every column. Fine for exploring; in real code prefer "
               "naming columns so the result stays stable if the table changes."),
    dict(id="L1Q4", lesson=1, type="sql",
         prompt="From employees, show first_name and last_name, but the first_name "
                "column must be labelled  given_name  in the output.",
         solution="SELECT first_name AS given_name, last_name FROM employees;",
         check_columns=["given_name", "last_name"],
         hint="Use:  first_name AS given_name",
         teach="AS renames a column in the RESULT only. The stored column is still first_name."),
    dict(id="L1Q5", lesson=1, type="sql",
         prompt="From departments, show dept_name and a computed column called "
                "budget_in_thousands equal to budget divided by 1000.",
         solution="SELECT dept_name, budget / 1000 AS budget_in_thousands FROM departments;",
         check_columns=["dept_name", "budget_in_thousands"],
         hint="You can do math in SELECT:  budget / 1000 AS budget_in_thousands",
         teach="SELECT can hold expressions, not only stored columns; each is evaluated "
               "once per row. Note: integer / integer gives an integer in SQLite."),
    dict(id="L1Q6", lesson=1, type="sql",
         prompt="For every employee, produce a single column called full_name that is "
                "the first name, a space, then the last name.",
         solution="SELECT first_name || ' ' || last_name AS full_name FROM employees;",
         check_columns=["full_name"],
         hint="Glue text with || :  first_name || ' ' || last_name",
         teach="|| concatenates strings. Remember the literal space ' ' in the middle."),

    # ---- Lesson 2 --------------------------------------------------------
    dict(id="L2Q1", lesson=2, type="mcq",
         prompt="Which clause correctly keeps only employees earning more than 100000?",
         choices=["WHERE salary > 100000", "WHERE salary => 100000",
                  "HAVING salary > 100000", "WHERE salary IS > 100000"],
         answer="a",
         teach="WHERE <condition> filters rows. '=>' is not valid ('>=' is). HAVING "
               "filters groups (lesson 6), not individual rows."),
    dict(id="L2Q2", lesson=2, type="sql",
         prompt="List first_name, last_name and salary of employees whose salary is at "
                "least 100000.",
         solution="SELECT first_name, last_name, salary FROM employees WHERE salary >= 100000;",
         hint="'at least' means >= (the boundary value counts).",
         teach="WHERE runs once per row and keeps rows where the condition is TRUE. "
               ">= includes the boundary."),
    dict(id="L2Q3", lesson=2, type="sql",
         prompt="Show emp_id, first_name and job_title for everyone in the Engineering "
                "department (dept_id 1).",
         solution="SELECT emp_id, first_name, job_title FROM employees WHERE dept_id = 1;",
         hint="WHERE dept_id = 1",
         teach="Equality filter. Numbers need no quotes; text literals do ('Engineering')."),
    dict(id="L2Q4", lesson=2, type="sql",
         prompt="Show first_name and last_name of employees hired before 2020-01-01.",
         solution="SELECT first_name, last_name FROM employees WHERE hire_date < '2020-01-01';",
         hint="Dates are stored as 'YYYY-MM-DD' text and compare correctly with < and >.",
         teach="ISO date strings sort like real dates, so < / > work directly. 'before' "
               "means strictly < ."),
    dict(id="L2Q5", lesson=2, type="sql",
         prompt="Show first_name, last_name, job_title and salary of employees whose "
                "job_title is exactly 'Engineer' AND who earn more than 106000.",
         solution="SELECT first_name, last_name, job_title, salary FROM employees "
                  "WHERE job_title = 'Engineer' AND salary > 106000;",
         hint="Join two conditions with AND.",
         teach="AND requires both sides to be true. Each side must be a full comparison."),
    dict(id="L2Q6", lesson=2, type="sql",
         prompt="Show the project_name of projects whose budget is between 200000 and "
                "500000 inclusive.",
         solution="SELECT project_name FROM projects WHERE budget BETWEEN 200000 AND 500000;",
         hint="BETWEEN a AND b  includes both endpoints.",
         teach="BETWEEN 200000 AND 500000 is the same as >= 200000 AND <= 500000."),
    dict(id="L2Q7", lesson=2, type="sql",
         prompt="Show first_name and last_name of employees in Sales (dept_id 2) or "
                "Marketing (dept_id 3). Use IN.",
         solution="SELECT first_name, last_name FROM employees WHERE dept_id IN (2, 3);",
         hint="WHERE dept_id IN (2, 3)",
         teach="IN (...) is shorthand for a chain of OR equality checks."),
    dict(id="L2Q8", lesson=2, type="sql",
         prompt="Show first_name, last_name and email of employees whose last_name "
                "starts with the letter M. Use LIKE.",
         solution="SELECT first_name, last_name, email FROM employees WHERE last_name LIKE 'M%';",
         hint="LIKE 'M%'  - the % matches any run of characters.",
         teach="LIKE does pattern matching: % = any number of characters, _ = exactly one."),

    # ---- Lesson 3 --------------------------------------------------------
    dict(id="L3Q1", lesson=3, type="mcq",
         prompt="What does  ORDER BY salary DESC  do?",
         choices=["Filters to only the highest salary",
                  "Sorts the result with the highest salary first",
                  "Removes duplicate salary values",
                  "Keeps only the first salary row"],
         answer="b",
         teach="ORDER BY sorts the result. DESC = descending (largest / latest first); "
               "ASC (the default) = ascending."),
    dict(id="L3Q2", lesson=3, type="sql", ordered=True,
         prompt="Show first_name, last_name and salary of all employees, highest salary "
                "first.",
         solution="SELECT first_name, last_name, salary FROM employees ORDER BY salary DESC;",
         hint="ORDER BY salary DESC",
         teach="ORDER BY is applied after WHERE. DESC flips the sort direction."),
    dict(id="L3Q3", lesson=3, type="sql", ordered=True,
         prompt="Show the 3 highest-paid employees: first_name, last_name, salary.",
         solution="SELECT first_name, last_name, salary FROM employees "
                  "ORDER BY salary DESC LIMIT 3;",
         hint="Sort by salary DESC, then LIMIT 3.",
         teach="LIMIT caps the row count AFTER sorting, so 'ORDER BY salary DESC LIMIT 3' "
               "= the top 3 earners."),
    dict(id="L3Q4", lesson=3, type="sql",
         prompt="List the distinct locations that departments are in.",
         solution="SELECT DISTINCT location FROM departments;",
         hint="SELECT DISTINCT location ...",
         teach="DISTINCT removes duplicate rows from the result; with one column that "
               "gives the unique values."),
    dict(id="L3Q5", lesson=3, type="sql",
         prompt="List the distinct dept_id values that appear in the projects table.",
         solution="SELECT DISTINCT dept_id FROM projects;",
         hint="SELECT DISTINCT dept_id FROM projects",
         teach="DISTINCT considers the whole selected row - here just dept_id, so you get "
               "each department that owns at least one project, once."),
    dict(id="L3Q6", lesson=3, type="sql", ordered=True,
         prompt="Show first_name, last_name and hire_date of the 5 most recently hired "
                "employees, newest first.",
         solution="SELECT first_name, last_name, hire_date FROM employees "
                  "ORDER BY hire_date DESC LIMIT 5;",
         hint="Most recent = largest date = DESC, then LIMIT 5.",
         teach="Newest first means ORDER BY hire_date DESC; LIMIT 5 trims after the sort."),
    dict(id="L3Q7", lesson=3, type="sql", ordered=True,
         prompt="Show first_name, last_name, dept_id and salary, ordered by dept_id "
                "ascending and, within each department, by salary descending.",
         solution="SELECT first_name, last_name, dept_id, salary FROM employees "
                  "ORDER BY dept_id, salary DESC;",
         hint="ORDER BY dept_id, salary DESC  - the first key sorts, the second breaks ties.",
         teach="Multiple ORDER BY keys: rows are sorted by the first; rows tied on it are "
               "then sorted by the second. Each key has its own ASC/DESC."),

    # ---- Lesson 4 --------------------------------------------------------
    dict(id="L4Q1", lesson=4, type="mcq",
         prompt="Which condition correctly finds employees with no manager?",
         choices=["WHERE manager_id = NULL", "WHERE manager_id IS NULL",
                  "WHERE manager_id == NULL", "WHERE manager_id != 0"],
         answer="b",
         teach="NULL means 'unknown'. Nothing equals NULL - not even NULL - so = NULL is "
               "never true. Use IS NULL / IS NOT NULL."),
    dict(id="L4Q2", lesson=4, type="sql",
         prompt="Show first_name and last_name of employees who have no manager.",
         solution="SELECT first_name, last_name FROM employees WHERE manager_id IS NULL;",
         hint="WHERE manager_id IS NULL",
         teach="IS NULL is the only correct test for a missing value."),
    dict(id="L4Q3", lesson=4, type="sql",
         prompt="Show the project_name of projects that are still running (no end date).",
         solution="SELECT project_name FROM projects WHERE end_date IS NULL;",
         hint="A running project has end_date IS NULL.",
         teach="Here a NULL end_date is used to mean 'no end yet'. IS NULL finds them."),
    dict(id="L4Q4", lesson=4, type="sql",
         prompt="Show first_name and last_name of employees who ARE assigned to a "
                "department.",
         solution="SELECT first_name, last_name FROM employees WHERE dept_id IS NOT NULL;",
         hint="WHERE dept_id IS NOT NULL",
         teach="IS NOT NULL keeps only rows that actually have a value."),
    dict(id="L4Q5", lesson=4, type="mcq",
         prompt="projects has 6 rows. SELECT COUNT(*) FROM projects WHERE end_date <> "
                "'2022-12-31'; returns 2, not 5. Why?",
         choices=["<> is invalid SQL",
                  "Rows where end_date is NULL make the condition UNKNOWN, so they are excluded",
                  "COUNT(*) skips NULLs",
                  "There are only 2 projects"],
         answer="b",
         teach="A comparison with NULL yields UNKNOWN, and WHERE keeps only TRUE rows. To "
               "include them you'd add  OR end_date IS NULL ."),
    dict(id="L4Q6", lesson=4, type="sql",
         prompt="Show first_name, last_name and the manager_id for every employee, but "
                "show 0 instead of NULL. Name that column manager_or_zero.",
         solution="SELECT first_name, last_name, COALESCE(manager_id, 0) AS manager_or_zero "
                  "FROM employees;",
         check_columns=["first_name", "last_name", "manager_or_zero"],
         hint="COALESCE(manager_id, 0) returns manager_id, or 0 when it is NULL.",
         teach="COALESCE(a, b, ...) returns its first non-NULL argument - handy for "
               "supplying a default in the result."),
]

FORBIDDEN = ("insert", "update", "delete", "drop", "alter", "create", "replace", "attach")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def say(text, indent=""):
    for para in text.split("\n"):
        if para.strip():
            print(textwrap.fill(para, width=90, initial_indent=indent,
                                subsequent_indent=indent))
        else:
            print()


def rule(char="-"):
    print(char * 60)


def print_table(cols, rows, limit=8):
    if not cols:
        print("    (no columns)")
        return

    def cell(v):
        return "NULL" if v is None else str(v)

    shown = rows[:limit]
    grid = [cols] + [[cell(v) for v in r] for r in shown]
    widths = [max(len(row[i]) for row in grid) for i in range(len(cols))]
    for gi, row in enumerate(grid):
        print("    " + " | ".join(val.ljust(widths[i]) for i, val in enumerate(row)))
        if gi == 0:
            print("    " + "-+-".join("-" * w for w in widths))
    if len(rows) > limit:
        print(f"    ... {len(rows) - limit} more row(s)")
    print(f"    [{len(rows)} row(s)]")


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def ensure_db():
    if not os.path.exists(DB_PATH):
        say("practice.db not found - building it now...")
        import setup_db
        setup_db.main()


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def run_query(conn, sql):
    try:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return dict(ok=True, cols=cols, rows=rows)
    except sqlite3.Error as e:
        return dict(ok=False, error=str(e))


def show_schema(conn):
    for (t,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        print(f"\n  {t}")
        for _cid, name, ctype, notnull, _dflt, pk in conn.execute(f"PRAGMA table_info({t})"):
            tags = []
            if pk:
                tags.append("pk")
            if notnull:
                tags.append("not null")
            print(f"    {name:16} {ctype}" + (f"  ({', '.join(tags)})" if tags else ""))
    print()


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------
def _is_read_only(sql):
    low = " " + re.sub(r"\s+", " ", sql.lower()) + " "
    return not any(f" {w} " in low or low.startswith(w + " ") for w in FORBIDDEN)


def _key(rows):
    # stable sort key that tolerates mixed types / None
    return sorted(rows, key=lambda r: [("~" if v is None else type(v).__name__ + repr(v))
                                       for v in r])


def _loose(rows):
    return sorted(tuple(sorted("" if v is None else str(v) for v in r)) for r in rows)


def grade_sql(conn, q, sql):
    """Return (ok: bool, message: str, student_result_or_None)."""
    if not _is_read_only(sql):
        return False, "This question only needs a SELECT. (Your answer looks like it changes data.)", None

    stu = run_query(conn, sql)
    if not stu["ok"]:
        return False, f"Your query did not run:\n    {stu['error']}", None

    sol = run_query(conn, q["solution"])
    ordered = q.get("ordered", False)
    want_cols = [c.lower() for c in q.get("check_columns", [])]
    got_cols = [c.lower() for c in stu["cols"]]

    s_rows = stu["rows"] if ordered else _key(stu["rows"])
    x_rows = sol["rows"] if ordered else _key(sol["rows"])

    if s_rows == x_rows:
        if want_cols and got_cols != want_cols:
            return False, ("Right rows - but the output columns must be exactly: "
                           f"{', '.join(q['check_columns'])}. You returned: "
                           f"{', '.join(stu['cols'])}. Use AS to name them."), stu
        if len(stu["cols"]) != len(sol["cols"]):
            return False, (f"Close - you returned {len(stu['cols'])} column(s); the "
                           f"question asks for {len(sol['cols'])}. Select only what is "
                           "asked."), stu
        return True, "", stu

    if _loose(stu["rows"]) == _loose(sol["rows"]):
        return False, ("The values are right, but the column order or naming does not "
                       f"match. Expected columns, in order: {', '.join(sol['cols'])}."), stu

    ns, nx = len(stu["rows"]), len(sol["rows"])
    if ns != nx:
        if ns == 0:
            why = "Your filter removed every row - check the operator, quotes or spelling."
        elif ns > nx:
            why = "Your filter is letting too many rows through - the condition is too loose."
        else:
            why = "Your filter is too strict, or missing a case."
        return False, f"Expected {nx} row(s); your query returned {ns}. {why}", stu

    if ordered and _key(stu["rows"]) == _key(sol["rows"]):
        return False, "Right rows, wrong order - check your ORDER BY.", stu

    diffs = [f"      {a}   ->   {b}" for a, b in zip(s_rows, x_rows) if a != b][:4]
    return False, ("Same number of rows, but some values differ (yours -> expected):\n"
                   + "\n".join(diffs)), stu


def grade_mcq(q, letter):
    letter = (letter.strip().lower() + " ")[0]
    return letter == q["answer"], f"Correct answer: {q['answer'].upper()})"


# ---------------------------------------------------------------------------
# Progress file
# ---------------------------------------------------------------------------
def load_progress():
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return dict(student="Sasi",
                created=_dt.date.today().isoformat(),
                lesson=1,
                completed_lessons=[],
                attempts=[])


def save_progress(prog):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(prog, f, indent=2)


def show_status(prog):
    rule("=")
    print(f"  {prog['student']}'s SQL progress   (started {prog['created']})")
    rule("=")
    for n, title in LESSONS.items():
        done = n in prog["completed_lessons"]
        cur = n == prog["lesson"]
        mark = "[x]" if done else ("[>]" if cur else "[ ]")
        best = max((a["score"] for a in prog["attempts"] if a["lesson"] == n), default=None)
        best_s = f"  best {best*100:4.0f}%" if best is not None else ""
        print(f"  {mark} Lesson {n}: {title}{best_s}")
    rule()
    if prog["attempts"]:
        print("  Recent attempts:")
        for a in prog["attempts"][-6:]:
            res = "PASS" if a["passed"] else "retry"
            print(f"    {a['ts'][:16].replace('T', ' ')}  L{a['lesson']}  "
                  f"{a['score']*100:4.0f}%  {res}")
    nxt = prog["lesson"]
    if nxt in LESSONS:
        print(f"\n  Next up: Lesson {nxt} - {LESSONS[nxt]}   (run:  py tutor.py)")
    else:
        print("\n  All loaded lessons complete. Ask Claude to add the next batch.")
    rule()


# ---------------------------------------------------------------------------
# Interaction
# ---------------------------------------------------------------------------
class Quit(Exception):
    pass


def read_sql_answer():
    print("  Enter your SQL, then a blank line to run it.  (:hint  :schema  :skip  "
          ":solution  :quit)")
    lines = []
    while True:
        try:
            raw = input("  sql> " if not lines else "     > ")
        except EOFError:
            raise Quit
        s = raw.strip()
        if not lines and s.startswith(":"):
            return s.lower(), None
        if not s:
            if lines:
                break
            continue
        lines.append(raw)
    return None, "\n".join(lines).strip().rstrip(";").strip()


def ask_mcq(q):
    say(q["prompt"])
    for i, choice in enumerate(q["choices"]):
        print(f"    {chr(97 + i)}) {choice}")
    while True:
        try:
            ans = input("  your answer (letter): ").strip()
        except EOFError:
            raise Quit
        if ans.lower() in (":quit", ":q"):
            raise Quit
        if ans:
            break
    ok, msg = grade_mcq(q, ans)
    print()
    if ok:
        print("  [OK] Correct.")
    else:
        print(f"  [X] Not quite. {msg}")
    say(q["teach"], indent="      ")
    return 1.0 if ok else 0.0


def ask_sql(conn, q):
    say(q["prompt"])
    attempt = 1
    while attempt <= 3:
        cmd, sql = read_sql_answer()
        if cmd:
            if cmd in (":quit", ":q"):
                raise Quit
            if cmd == ":schema":
                show_schema(conn)
            elif cmd == ":hint":
                say("hint: " + q.get("hint", "(no hint for this one)"), indent="  ")
            elif cmd == ":skip":
                print("  Skipped.")
                say("A correct answer:\n    " + q["solution"], indent="  ")
                say(q["teach"], indent="      ")
                return 0.0
            elif cmd == ":solution":
                say("A correct answer:\n    " + q["solution"], indent="  ")
                say(q["teach"], indent="      ")
                return 0.0
            else:
                print(f"  unknown command {cmd!r}")
            continue

        if not sql:
            continue

        ok, msg, stu = grade_sql(conn, q, sql)
        if stu is not None:
            print("\n  Your result:")
            print_table(stu["cols"], stu["rows"])
        if ok:
            print(f"\n  [OK] Correct!  (attempt {attempt})")
            if q.get("teach"):
                say(q["teach"], indent="      ")
            return ATTEMPT_WEIGHT[attempt]

        print()
        say("[X] " + (msg or "Not a match yet."), indent="  ")
        if attempt == 2 and q.get("hint"):
            say("hint: " + q["hint"], indent="  ")
        if attempt < 3:
            print("  Try again.\n")
        attempt += 1

    print()
    say("Here is a correct answer:\n    " + q["solution"], indent="  ")
    say(q["teach"], indent="      ")
    return 0.0


def ask_question(conn, q, idx, total):
    print()
    rule()
    print(f"  Question {idx}/{total}   [{q['id']}]")
    rule()
    if q["type"] == "mcq":
        return ask_mcq(q)
    return ask_sql(conn, q)


def run_lesson(conn, prog, lesson):
    qs = [q for q in QUESTIONS if q["lesson"] == lesson]
    if not qs:
        say(f"No questions loaded for lesson {lesson}. Ask Claude to add them.")
        return

    print()
    rule("=")
    print(f"  LESSON {lesson}: {LESSONS[lesson]}")
    print(f"  {len(qs)} questions. Pass mark {int(PASS_MARK*100)}%.")
    rule("=")

    scores = {q["id"]: ask_question(conn, q, i, len(qs)) for i, q in enumerate(qs, 1)}

    rnd = 1
    while True:
        avg = sum(scores.values()) / len(scores)
        passed = avg >= PASS_MARK

        print()
        rule("=")
        print(f"  LESSON {lesson} RESULT (round {rnd}):  {avg*100:.0f}%   "
              f"{'PASS' if passed else 'not yet - need ' + str(int(PASS_MARK*100)) + '%'}")
        rule("=")
        for q in qs:
            s = scores[q["id"]]
            tag = "ok  " if s >= 1.0 else ("part" if s > 0 else "MISS")
            print(f"    [{tag}] {q['id']}  {s:.1f}")

        prog["attempts"].append(dict(
            ts=_dt.datetime.now().isoformat(timespec="seconds"),
            lesson=lesson, round=rnd, score=round(avg, 3), passed=passed,
            per_question={k: round(v, 2) for k, v in scores.items()}))
        save_progress(prog)

        if passed or rnd >= 3:
            break

        weak = [q for q in qs if scores[q["id"]] < 1.0]
        print()
        say(f"Let's re-drill the {len(weak)} you missed. Read these first:")
        for q in weak:
            print(f"\n  {q['id']} - {q['teach']}")
        try:
            input("\n  Press Enter to retry those questions... ")
        except EOFError:
            raise Quit
        for i, q in enumerate(weak, 1):
            scores[q["id"]] = ask_question(conn, q, i, len(weak))
        rnd += 1

    if passed:
        if lesson not in prog["completed_lessons"]:
            prog["completed_lessons"].append(lesson)
        prog["lesson"] = lesson + 1
        save_progress(prog)
        print()
        if lesson + 1 in LESSONS:
            say(f"Lesson {lesson} cleared. Next time you'll start Lesson {lesson + 1}: "
                f"{LESSONS[lesson + 1]}.")
        else:
            say(f"Lesson {lesson} cleared - and that's the last lesson loaded so far. "
                f"Ask Claude to add the next batch.")
    else:
        save_progress(prog)
        print()
        say(f"Not there yet - progress saved. Run  py tutor.py  again to retry Lesson "
            f"{lesson}. Between sessions, practise freely with  py q.py .")


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def selftest():
    ensure_db()
    conn = connect()
    bad = 0
    for q in QUESTIONS:
        if q["type"] != "sql":
            continue
        r = run_query(conn, q["solution"])
        if not r["ok"]:
            bad += 1
            print(f"  FAIL {q['id']}: {r['error']}")
        else:
            print(f"  ok   {q['id']}: {len(r['rows'])} row(s), cols={r['cols']}")
    print("\nselftest:", "all reference answers run" if not bad else f"{bad} FAILED")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(add_help=True, description="Interactive SQL tutor")
    ap.add_argument("--status", action="store_true", help="show progress and exit")
    ap.add_argument("--reset", action="store_true", help="wipe progress and exit")
    ap.add_argument("--lesson", type=int, help="start at a specific lesson number")
    ap.add_argument("--selftest", action="store_true", help="run every reference answer")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if args.reset:
        if os.path.exists(PROGRESS_PATH):
            os.remove(PROGRESS_PATH)
        print("Progress wiped. Run  py tutor.py  to start fresh.")
        return

    ensure_db()
    prog = load_progress()

    if args.status:
        show_status(prog)
        return

    lesson = args.lesson or prog["lesson"]
    if lesson not in LESSONS:
        show_status(prog)
        return

    conn = connect()
    print()
    say(f"Welcome back, {prog['student']}. Starting Lesson {lesson}.  "
        f"(Ctrl+C or :quit saves and exits.)")
    try:
        run_lesson(conn, prog, lesson)
    except (Quit, KeyboardInterrupt):
        save_progress(prog)
        print("\n\nSaved. See you next time - run  py tutor.py  to continue.")
    finally:
        conn.close()
    print()
    show_status(load_progress())


if __name__ == "__main__":
    main()
