# SQL_Writer

An interactive, self-grading **technical-literacy course** — six modules: SQL,
reading JSON, reading API docs, reading logs/errors, AI-assisted investigation,
and config-vs-code judgement. You work through exercises in the terminal; the
tutor checks each answer, explains what was wrong, and paces the lessons to how
you're doing.

**Built so far: Module 1 (SQL).** You write real SQL against a real database and
the tutor runs it. The other modules are on the roadmap.

> **Full context — what this project is and why it's built this way — lives in
> [PROJECT_STATUS.md](PROJECT_STATUS.md). Read that first.** This README is only
> how to install and run it.

## Requirements

- Windows with the **`py`** launcher (Python 3.x). Check: `py --version`.
- Nothing else. No pip installs — the course uses only the Python standard
  library and its bundled SQLite.

> Use `py`, not `python`. On this setup bare `python` resolves to a Windows Store
> stub and fails with "Permission denied".

## Setup

From the repo folder:

```
py setup_db.py
```

Creates `practice.db` (a small fictional-company database). Re-run any time to
reset it to a clean state.

## Run the course

```
py tutor.py
```

Asks questions, grades each answer, and resumes where you left off.

| Command | What it does |
|---------|--------------|
| `py tutor.py` | Start / resume the course |
| `py tutor.py --status` | Show your scores and current lesson |
| `py tutor.py --lesson 3` | Jump to a specific lesson |
| `py tutor.py --reset` | Wipe progress and start over |
| `py tutor.py --selftest` | (maintenance) run every reference answer |

While answering an SQL question, type one of these instead of a query:

| In-question command | Effect |
|---------------------|--------|
| `:hint` | Show a hint |
| `:schema` | List all tables and columns |
| `:skip` | Give up on this question (scores 0) |
| `:solution` | Reveal a correct answer (scores 0) |
| `:quit` | Save and exit |

**Scoring:** SQL question — correct on the 1st / 2nd / 3rd try scores
1.0 / 0.7 / 0.4. Multiple choice — 1.0 or 0.0. A lesson passes at 80% average;
below that, the questions you missed are re-drilled.

Your progress is saved to `progress.json` between runs.

## Free practice (no grading)

```
py q.py "SELECT * FROM employees LIMIT 5"     # one-liner
py q.py scratch.sql                            # run a file you edit
py q.py                                        # interactive REPL; end statements with ;
py q.py --schema                               # list every table and column
```

## The practice database

A small fictional company:

| Table | Columns |
|-------|---------|
| `departments` | dept_id, dept_name, location, budget |
| `employees` | emp_id, first_name, last_name, dept_id, job_title, salary, hire_date, manager_id, email |
| `projects` | project_id, project_name, dept_id, start_date, end_date (NULL = ongoing), budget |
| `employee_projects` | emp_id, project_id, role, hours_allocated |

16 employees, 4 departments, 6 projects. Some employees have no manager, one has
no department, some projects have no end date — so NULLs and joins have
something to work with.
