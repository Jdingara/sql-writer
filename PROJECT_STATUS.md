# PROJECT_STATUS.md

The persistent memory and **single source of truth** for this project. If any
other file (README, code comments, anything) disagrees with this file, this file
is correct and the other file should be fixed to match.

Both CLAUDE.md and AGENTS.md point every AI tool here first, and require this
file's "Current Status" and "Open Decisions" sections to be updated at the end
of any meaningful work session.

---

## Goal

SQL_Writer is a personal, self-paced **technical-literacy course** for Sasi, who
comes from an ERP / functional background and is building the technical skills
for a more technical role — one that works alongside developers without being a
developer (reading job descriptions fluently, handling technical interviews,
investigating problems before escalating them).

It is an interactive, self-grading tutor. Scope is **six modules**, done in
order: (1) SQL — intermediate; (2) reading JSON; (3) reading API documentation;
(4) reading logs & error messages; (5) the AI-assisted investigation habit;
(6) configuration-vs-code judgement. It deliberately stops short of software
engineering — no production code, system design, or algorithms.

Module 1 (SQL) is the part built so far: it asks a question, runs the learner's
SQL against a local SQLite database, checks the result, explains what was wrong,
teaches the concept, and adapts pacing to quiz performance. Modules 2–6 will
reuse the same tutor engine with additional question types.

---

## Core Decisions / Rules

_Decided and stable. Do not change any of these without explicit user
confirmation._

1. **Python via the `py` launcher only.** Bare `python` / `python3` is blocked on
   this machine (Windows Store execution alias → "Permission denied"). Every
   command, script shebang-equivalent, and doc line uses `py`.
2. **Standard library only. No third-party packages.** `sqlite3`, `argparse`,
   `json`, `textwrap`, `re`, `datetime` — all bundled. Setup must stay
   zero-install.
3. **Engine: SQLite**, through Python's bundled `sqlite3` module (engine
   3.50.4). One database file, `practice.db`.
4. **The practice dataset is deterministic and frozen.** It is hand-written in
   `setup_db.py` (no randomness) so every quiz has one known-correct result.
   Changing the data means updating every affected reference answer and running
   `py tutor.py --selftest`. Do not randomize or casually extend it.
5. **The dataset's NULLs and gaps are intentional** and must not be "cleaned up":
   Paula Clark (emp 16) has `dept_id = NULL`; projects Boreas/Cronus/Eos have
   `end_date = NULL`; Alice/Frank/Jack/Mia/Paula have `manager_id = NULL`;
   employees Ivy/Mia/Nina/Paula have no `employee_projects` rows. These make the
   NULL, LEFT JOIN, and anti-join lessons real.
6. **Primary interface: Claude drives the course in chat** (changed 2026-09-03 —
   see Current Status). Claude poses one question at a time, Sasi runs SQL in a
   tool of their choice, pastes query + result, Claude grades and teaches. `q.py`
   is the SQL runner. `tutor.py` is kept for optional strict self-drill and as
   the store of question content, but is no longer the day-to-day path.
7. **Grading is on understanding, not exact strings.** A right idea with a typo
   (`project` for `projects`, `''` for `' '`) is "correct, fix the typo" — not a
   fail. `tutor.py`'s numeric 1.0 / 0.7 / 0.4 model still applies *if* that tool
   is used, but the chat-driven mode grades pass / almost / revisit and moves on
   when the concept is solid.
8. **`tutor.py` internal checking** (only relevant when that tool is run):
   compares result sets order-insensitive unless `ordered=True`; `check_columns`
   enforces output column names; a loose all-strings pass yields the "right
   data, wrong column order/name" hint.
9. **Progress is tracked in this file** — the "Module 1 progress" table under
   Current Status. `progress.json` (written by `tutor.py`) is only meaningful on
   sessions where that tool was used.
10. **Curriculum is organised as six modules** (see Full Roadmap). Within a
    module, lessons/exercises are added to `tutor.py` incrementally as the
    learner reaches them, not all at once.
11. **Audience voice:** written for a beginner who types fast and informally.
    Explanations stay short, plain, and example-first.
12. **Scope = six technical-literacy modules, in this order** (each feeds the
    next — JSON before API docs, API docs before reading API logs, everything
    before the config-vs-code judgement call): (1) SQL intermediate — in
    progress; (2) Reading JSON; (3) Reading API documentation; (4) Reading logs
    & error messages; (5) AI-assisted investigation habit; (6)
    Configuration-vs-code judgement.
13. **Explicitly out of scope** — do not build these even if they come up in
    passing; confirm with Sasi first: writing production code, system design,
    algorithms / DSA, building APIs or services. The ceiling is "read,
    interpret, sanity-check, and describe a problem accurately when escalating."
14. **The SQL module target is intermediate:** `SELECT`, `WHERE`, `JOIN`,
    `GROUP BY` / aggregates — enough to pull data and sanity-check numbers
    unaided. Lessons 1–8 are the core. Lesson 9 (subqueries / CTEs) is optional.
    Window functions, DDL, and performance tuning are **cut** unless Sasi asks —
    they are past the target.
15. **Under version control since 2026-09-30.** `git init` done, everything
    committed (including `practice.db` and `progress.json` — both small and
    fine to track). No `.gitignore` needed yet beyond Python cache files. GitHub
    remote is pending Sasi's `gh auth login` (see Open Decisions).

---

## Non-Obvious Technical Findings

_Things already discovered the hard way. Don't rediscover them._

- **`python` is a trap on this machine.** `python`/`python3` resolve to
  `...\WindowsApps\python` and return "Permission denied" (Store alias, not an
  interpreter). `py` (Python launcher, 3.14.3) is the real one. The `sqlite3`
  **CLI is not installed at all** — only the Python module exists, which is why
  `q.py` / `tutor.py` wrap it.
- **SQLite integer division.** `int / int` is integer division:
  `800000 / 1000000` → `0`. Lesson 1 Q5 deliberately divides by `1000` for clean
  integers and its teach note flags this. For a decimal result, divide by a
  float (`/ 1000.0`).
- **SQLite sorts `NULL` first** in `ORDER BY ... ASC`. Lesson 3 Q7
  (`ORDER BY dept_id, salary DESC`) returns Paula (NULL `dept_id`) first.
  Reference and student queries share the ORDER BY so it still matches — but keep
  it in mind when authoring ordered questions.
- **`NULL` comparisons yield UNKNOWN, and `WHERE` keeps only TRUE rows**, so
  `WHERE end_date <> 'x'` silently drops the 3 NULL-`end_date` projects. This is
  the whole point of Lesson 4 and the answer to its Q5.
- **`q.py` splits on `;`** to run multi-statement files/pastes. A `;` inside a
  string literal would break that. Fine for current lessons; known limitation.
- **`q.py`'s module docstring must stay a raw string** (`r"""..."""`) because it
  contains `\schema` / `\tables`; otherwise Python 3.14 emits
  `SyntaxWarning: invalid escape sequence`.
- **`tutor.py` grading uses a hand-rolled sort key**
  (`type(v).__name__ + repr(v)`, `"~"` for `None`) because plain `sorted()` on
  result tuples containing a mix of `None` and `int` raises `TypeError` in
  Python 3.
- **`tutor.py` refuses to run** a query containing
  `insert/update/delete/drop/alter/create/replace/attach` before executing it, so
  a learner cannot damage `practice.db` mid-lesson. The DB is also cheap to
  rebuild: `py setup_db.py`.
- **`py tutor.py --selftest`** runs every SQL reference answer against the DB and
  prints row counts. Run it after any edit to `setup_db.py` or the question bank.

---

## Full Roadmap

Six modules, in order. All run through `tutor.py`; Modules 2–6 need new question
types added to the engine first (see Open Decisions).

### Module 1 — SQL (intermediate)  ·  in progress

| Lesson | Topic | Status |
|--------|-------|--------|
| 1 | SELECT / FROM / column lists / aliases / expressions (6 Q) | **Done** |
| 2 | WHERE: `=`, comparisons, `AND`/`OR`, `BETWEEN`, `IN`, `LIKE` (8 Q) | **Done** |
| 3 | ORDER BY / LIMIT / DISTINCT (7 Q) | **Done** |
| 4 | NULL / `IS NULL` / `IS NOT NULL` / `COALESCE` (6 Q) | **Done** |
| 5 | Aggregates: `COUNT` / `SUM` / `AVG` / `MIN` / `MAX` | Not started |
| 6 | `GROUP BY` and `HAVING` | Not started |
| 7 | `INNER JOIN` | Not started |
| 8 | `LEFT JOIN` and anti-joins (`WHERE x IS NULL`) — **module core ends here** | Not started |
| 9 | Subqueries and CTEs (`WITH`) | Optional |
| — | Set operators, `CASE`, window functions, `INSERT`/`UPDATE`/`DELETE`, `CREATE TABLE`, performance | **Cut** (past target — build only if asked) |

### Modules 2–6 — technical literacy

| # | Module | Grading approach | Status |
|---|--------|------------------|--------|
| 2 | **Reading JSON** — objects, arrays, nesting, data types; walking a path like `data.items[0].name` | show a JSON blob → ask for a value / count / type (`json` / `short` question type) | Not started |
| 3 | **Reading API documentation** — endpoint, base URL, path & query params; GET vs POST vs PUT/DELETE; status codes (2xx / 4xx yours / 5xx theirs); auth headers at recognition level | doc-snippet + `mcq` ("which endpoint / method / what does this 401 mean") | Not started |
| 4 | **Reading logs & error messages** — anatomy of an error (level, message, stack trace, "caused by"); read last line first; classify: timeout vs connection-refused vs permission vs not-found vs bad-data vs rate-limit | paste a log → `classify` (mcq) + short "how would you escalate this" | Not started |
| 5 | **AI-assisted investigation habit** — paste error + what you did + expected + actual + what changed; ask for likely causes not just a fix; verify the answer against the real system; spot when the AI is guessing | scenario → draft the investigation prompt → checklist / rubric score | Not started |
| 6 | **Configuration-vs-code judgement** — the spectrum from settings toggle → admin config → low-code → needs a developer → needs architecture; signs of each; applied to unfamiliar platforms & JDs | scenario → "config or code?" → justify (`mcq` + short) | Not started |

### Engine work (enables Modules 2–6)

| Item | Status |
|------|--------|
| Generalise `tutor.py`: `module` dimension in `progress.json`; question types `short`, `json`, `classify`, `prompt-craft` | Not started |
| Cross-module spaced repetition of missed questions | Idea only |

---

## Current Status

**Last updated: 2026-10-05**

### 2026-10-05 — Session 6 complete: Lesson 7 (JOIN) done

Finished Lesson 7 after the git checkpoint. Q6 (`employees` ⨝ `employee_projects`,
17 rows) correct first try. Lesson total: 5 of 6 clean first try; the one
non-clean item was double-quoted text (`"Engineering"`) — correct result in
SQLite, but fixed to single quotes as the rule going forward. Report card 70 → 77/100.
Only **Lesson 8 (LEFT JOIN / anti-joins)** remains for full target coverage. Docs
(`LEARNING_LOG.md`, `report.html`, this file) updated and committed/pushed to
https://github.com/Jdingara/sql-writer.

### 2026-09-30 — Session 6 (in progress): Lesson 7 (JOIN), git init

Chat-driven, DBeaver. Lesson 7 underway: Q1–Q5 all correct (Q2–Q3 first try;
Q4 correct despite using double-quoted `"Engineering"` for a string literal —
flagged as SQLite-only leniency, real databases want single quotes; Q5 combines
JOIN + GROUP BY correctly). Q6 (join `employees` to `employee_projects`) is
outstanding — session paused mid-lesson at Sasi's request to set up version
control. Score/report card **not yet updated** for this session — that happens
once Lesson 7 (or the whole JOIN pair, Lessons 7–8) is complete, to avoid a
premature mid-lesson number.

At Sasi's request, the repo is now a **git repository**: `git init`, full commit
of all files (see Core Decision 15), branch renamed to `main`, remote
**https://github.com/Jdingara/sql-writer** added and pushed successfully (Sasi
created the empty repo via the GitHub web UI; `git push` worked without needing
`gh auth login` — Git Credential Manager handled it). Repo is public/private per
Sasi's own choice on GitHub — not tracked here, check the repo settings if it
matters later.

### 2026-09-23 — Session 5: Lesson 6 (GROUP BY / HAVING) complete

Chat-driven, DBeaver, after a ~2-week gap. 5 of 7 correct first try; the 2 misses
were the two near-universal first-exposure `GROUP BY` confusions — mistaking it
for a sort (vs. `ORDER BY`), and trying to filter an aggregate with `WHERE` /
inside the `SELECT` list instead of `HAVING`. Both were resolved with one
explanation and are not flagged as a stuck pattern (no re-drill scheduled; watch
only if they recur). All prior watch-items held resolved. Report card 65 → 70/100
(mid "writes day-to-day SQL" band). **Only Lessons 7–8 (`JOIN`) remain** for full
Module-1 target coverage — expect the score to settle in the high-70s/low-80s
once done. `LEARNING_LOG.md` + `report.html` updated; "Session 5" row added.

### 2026-09-10 — Session 4: Lesson 5 (aggregates) complete

Chat-driven, DBeaver. `COUNT` / `SUM` / `AVG` / `MIN` / `MAX`, aggregate +
`WHERE`, aggregate + `AS` — every question essentially first try, no syntax
errors; the cleanest lesson so far. Opened with a NULL re-drill (answered
correctly), and the `COUNT(manager_id)` prediction question was answered right
*with unaided reasoning* — so the Session-3 NULL gap has closed and the concept
is transferring. Report card 57 → 65/100 (solidly in the "writes day-to-day SQL"
band). What's left for the target: Lesson 6 (`GROUP BY`/`HAVING`) and Lessons 7–8
(`JOIN`). `LEARNING_LOG.md` + `report.html` updated; "Session 4" row added to the
history table.

### 2026-09-09 — Session 3: Lesson 4 (NULL) complete

Chat-driven, DBeaver. All four NULL **query** questions correct first try, no
syntax slips — `IS NULL`, `IS NOT NULL`, `COALESCE(col, 0) AS alias`. Both
**concept / MCQ** questions were missed: chose `= NULL` over `IS NULL` right after
the rule was stated, and misread `<>` while reasoning about why NULL rows drop
out of a filter. Takeaway: NULL three-valued logic (comparisons yield UNKNOWN,
`WHERE` keeps only TRUE) has not stuck — Session 4 should open with a quick
re-drill of it. Report card 52 → 57/100 (just into the "writes day-to-day SQL"
band, lower edge; coverage still only 42 — aggregates/GROUP BY/JOIN are the jump).
Concrete demo tables (showing TRUE/FALSE/UNKNOWN per row) landed better than the
abstract rule — reuse that teaching approach. `LEARNING_LOG.md` + `report.html`
updated; a "Session 3" row was added to the history table.

### 2026-09-04 — Session 2: Lessons 2 (WHERE) and 3 (ORDER BY/LIMIT/DISTINCT) complete

Chat-driven, DBeaver, one continuous sitting. Lesson 2: all 8 correct
(`=`/`>`/`<`, `AND`/`OR`, `BETWEEN`, `IN`, `LIKE`); weak spot was incomplete
queries (a bare `WHERE` fragment, a missing column, a missing second condition —
all self-corrected). Lesson 3: 6 of 7 correct first try, including a multi-column
`ORDER BY dept_id, salary DESC` with no errors — the best rate so far; the one
miss was a forgotten `DESC`. Trailing-`s` table-name typos (Session 1's #1 issue)
stayed at zero across both lessons — considered fixed. Report card 30 → 41 → 52
(now right at the edge of the "writes day-to-day SQL" target band). Next: Lesson
4 (NULL). `LEARNING_LOG.md` + `report.html` updated in place for this session.

### 2026-09-03 — switched Module 1 to chat-driven tutoring

`tutor.py`'s terminal UX did not work for Sasi in practice:

- **Exact-match grading punished typos.** Lesson 1 scored **52%** almost entirely
  on spelling slips (`project` vs `projects`, `''` vs `' '`, `departsments`), not
  concept errors — Sasi understood the material. A brittle grader reads as
  failure and is demoralising.
- **Ctrl+C (reflex for copy) kills the program.** In a terminal it interrupts,
  and because only the lesson pointer is saved, re-running restarts the lesson
  from Q1. Sasi lost their place this way.
- **Terminal scrollback is unusable after ~30 questions** — earlier explanations
  can't be reviewed.

**New mode:** Claude runs the course in the chat. One question at a time here
(the conversation is the persistent, scrollable record); Sasi runs SQL in a tool
of their choice and pastes query + result; Claude grades on understanding
(typo-tolerant), teaches the fix, gives the next question. **Recommended SQL
tool: DB Browser for SQLite** (free GUI) — it opens `practice.db`, shows every
table/column in a sidebar (kills the name-typo problem), and has a Run-SQL pane.
`q.py` remains a valid runner. Progress lives in the "Module 1 progress" table
below.

`tutor.py`, `q.py`, `setup_db.py`, `practice.db` are all still valid; the
question bank inside `tutor.py` is still the content source for chat questions.
Sasi actually installed **DBeaver** (not DB Browser) and connected `practice.db`
— fine, same job; queries run with **Ctrl+Enter** there.

**Module 1 progress**

| Lesson | State |
|--------|-------|
| 1 — SELECT / FROM / aliases / expressions | ✅ Complete (Session 1). All 6 correct in DBeaver. |
| 2 — WHERE (`=` `>` `<`, `AND`/`OR`, `BETWEEN`, `IN`, `LIKE`) | ✅ Complete (Session 2, 2026-09-04). All 8 correct. |
| 3 — ORDER BY / LIMIT / DISTINCT | ✅ Complete (Session 2, same day). 6 of 7 correct first try — best rate yet. |
| 4 — NULL (IS NULL / IS NOT NULL / COALESCE) | ✅ Complete (Session 3, 2026-09-09). All 4 query questions first try; both concept/MCQ questions missed — NULL three-valued logic not stuck at the time. |
| 5 — Aggregates (COUNT/SUM/AVG/MIN/MAX) | ✅ Complete (Session 4, 2026-09-10). Cleanest lesson yet, near-zero errors; NULL re-drill passed and the idea transferred (predicted `COUNT(manager_id)`=11 with unaided reasoning). |
| 6 — GROUP BY / HAVING | ✅ Complete (Session 5, 2026-09-23). 5/7 first try; the 2 misses were the two textbook first-time confusions (GROUP BY-vs-ORDER BY, WHERE-vs-HAVING for aggregates) — expected, not concerning. |
| 7 — JOIN (two-table: INNER JOIN, aliases, JOIN+WHERE, JOIN+GROUP BY) | ✅ Complete (Session 6, 2026-10-05). 5/6 first try; 1 correct result with double-quoted text — flagged, use single quotes. |
| 8 — LEFT JOIN / anti-joins ("no match") | Next — last lesson for full target coverage |

Report card: S1=30, S2=52, S3=57, S4=65, S5=70, S6=**77/100** (solidly mid-"writes
day-to-day SQL"; only Lesson 8 — LEFT JOIN / anti-joins — left). Details in
`LEARNING_LOG.md` / `report.html`.

### 2026-09-03 — added a per-session learning log + visual report card

At Sasi's request, two artefacts, both refreshed every session:

- [`LEARNING_LOG.md`](LEARNING_LOG.md) — every question, every answer, ranked
  mistake patterns, what was learned, per session. Prose record.
- [`report.html`](report.html) — visual report card Sasi opens in a browser:
  **score out of 100** vs the job market, a four-metric breakdown (concept grasp
  / syntax accuracy / independence / market coverage — the last one gates the
  overall), focus areas, next plan, and a session-history table that grows one
  row per session so the trend is visible. Self-contained, light/dark, built
  with the `dataviz` skill's palette. **Claude overwrites this file at the end of
  every session** and keeps its numbers in sync with `LEARNING_LOG.md`.

Grading bands (0–30 getting started / 30–55 SQL-literate / **55–80 writes
day-to-day SQL ← target** / 80–100 developer-DBA out of scope). Session 1 score:
**30/100**.

### 2026-09-01 — scope expanded: "SQL course" → "technical-literacy course"

Sasi defined the real target (see Goal): six technical-literacy skills for a more
technical role, explicitly **not** software engineering. What changed:

- SQL is now **Module 1 of 6**, not the whole project. Modules 2–6 (JSON, API
  docs, logs/errors, AI-investigation, config-vs-code) are on the Roadmap, not
  yet built.
- The SQL module is **trimmed to an intermediate target** — core finish is
  through Lesson 8 (JOINs). Set operators, `CASE`, window functions, DML, DDL
  and performance are cut from scope; Lesson 9 (subqueries) is optional. This
  also makes two earlier Open Decisions (safe DML writes, a `salaries` table for
  window functions) mostly moot.
- **No code changed this step** — Sasi is mid-Lesson-1 in the terminal. Before
  Modules 2–6 can be authored, `tutor.py` needs generalising: new question types
  (JSON value-lookup, error classification, prompt-craft) and a `module`
  dimension in `progress.json`.
- Docs (this file), README, and cross-session memory updated to the new goal.

### 2026-09-01 — initial build

The repo went from empty to a working 4-lesson course in one session.

**Built and kept:**

- **Practice environment.** `setup_db.py` builds `practice.db`: a fictional
  company with `departments` (4 rows), `employees` (16), `projects` (6),
  `employee_projects` (17). All data hand-written and deterministic. `q.py` is a
  standalone runner — one-liner arg, `.sql` file, REPL, or `--schema`.
- **`tutor.py`, the self-grading course.** Design choices made this session and
  still in place:
  - Question bank is an inline list of dicts (`QUESTIONS`) tagged by `lesson`,
    plus a `LESSONS` title map. Chosen over separate data files to keep the whole
    course reviewable in one file while it is still small.
  - Grading runs the learner's SQL and a reference query and compares results;
    order-insensitive unless `ordered=True`; `check_columns` enforces alias
    names; a loose all-strings pass generates "right data, wrong column
    order/name" hints.
  - Adaptive loop: a sub-80% lesson re-drills only the missed questions, max 3
    rounds, then advances regardless (decision: never trap the learner).
  - Attempt-based partial credit (1.0 / 0.7 / 0.4) instead of binary per-question
    pass/fail, so "got it on the second try" shows up in the score.
  - `progress.json` holds persistent learner state; no Markdown file tracks live
    progress.
- **Verified.** `py tutor.py --selftest` passes — all 22 SQL reference answers
  execute and their row counts match hand calculations. Two full simulated
  lesson runs (Lessons 1 and 2, via piped stdin) exercised: correct answers, a
  wrong→right retry, `:hint`, partial credit, lesson pass, lesson advance, and
  `progress.json` persistence. All worked. Progress was then wiped
  (`py tutor.py --reset`) so the learner starts clean at Lesson 1.
- **Docs.** Added this 4-file persistent-memory system (PROJECT_STATUS.md +
  CLAUDE.md + AGENTS.md pointers + a rewritten README.md).

**Tried and reverted this session:**

- `grade_sql` originally printed the **expected** result table on a row-count
  mismatch. Removed — it handed the learner the answer on attempt 1. Now each
  attempt shows only the learner's **own** result; the full reference answer
  appears only after attempt 3 or an explicit `:solution`.
- An earlier standalone `PROGRESS.md` (a curriculum map) was **deleted**. Its
  content is now the "Full Roadmap" section above, so there is exactly one place
  that can be authoritative about lesson status.

**Not done yet:**

- Lessons 5–15 have no questions in `tutor.py`.
- `progress.json` does not exist until the learner first runs `py tutor.py`.
- No git repository initialised.

---

## Open Decisions

_Unresolved. One line of context each so the thread can be picked back up._

- **Generalising `tutor.py` for Modules 2–6.** Needs new question types: `short`
  (text/number match, tolerant of formatting/case), `json` (show a blob, ask for
  a value / count / type), error-`classify` (an `mcq` variant), and a
  prompt-craft type for Module 5. `progress.json` needs a `module` key alongside
  `lesson`. Approach not designed yet.
- **Module 5 (AI-assisted investigation) is hard to auto-grade.** Likely a
  checklist self-assessment ("did your prompt include what you did / expected /
  actual / what changed / a verification step?") rather than machine grading.
  Undecided.
- **SQL Lesson 9 (subqueries / CTEs): include or cut?** Currently optional.
  Decide when Sasi finishes Lesson 8.
- **Cross-module spaced repetition.** Should missed questions resurface later
  across modules, or is per-lesson re-drill enough? Leaning light; not built.
- ~~GitHub remote~~ **Resolved 2026-10-01.** Sasi created
  https://github.com/Jdingara/sql-writer (empty, via the web UI); `origin` added
  and pushed via plain `git push` (Git Credential Manager handled auth — `gh`
  itself is still not logged in, but wasn't needed). Branch is `main`.
- **(Mostly moot)** Safe DML writes and a `salaries` history table were open
  items for SQL Lessons 12–13 — those lessons are now cut from scope. Revisit
  only if Sasi asks for window functions or data-modification lessons.

---

## Repo Structure

| Path | What it does |
|------|--------------|
| `PROJECT_STATUS.md` | This file. Persistent project memory and single source of truth. |
| `CLAUDE.md` | Pointer for Claude Code: read PROJECT_STATUS.md first, update it after. Word-for-word identical to AGENTS.md. |
| `AGENTS.md` | Same pointer for other AI tools (Codex, Cursor, …). Kept word-for-word identical to CLAUDE.md. |
| `README.md` | Human-facing setup & usage only (how to run `tutor.py` / `q.py`, flags). Points here for context; carries no history/decisions. |
| `LEARNING_LOG.md` | Per-session record of Sasi's questions, answers, mistake patterns, and a market-readiness read. Updated by Claude at the end of each session. |
| `report.html` | Visual report card — score /100 vs the job market, score breakdown, focus areas, next plan, session-history table. Self-contained (no deps), light/dark. **Overwritten each session** by Claude; Sasi opens it in a browser. Data mirrors `LEARNING_LOG.md`. |
| `tutor.py` | Optional strict self-drill tool and the store of question content (`QUESTIONS` bank, `LESSONS` titles). Not the day-to-day path since 2026-09-03 (chat-driven now). CLI: `--status`, `--lesson N`, `--reset`, `--selftest`. |
| `q.py` | SQL runner Sasi uses to execute queries. One-liner / `.sql` file / REPL / `--schema`. (DB Browser for SQLite is the recommended alternative.) |
| `setup_db.py` | Creates / resets `practice.db` from hardcoded deterministic data. |
| `practice.db` | The SQLite database the learner queries. Module 1 (SQL) only. Regenerable; safe to delete. |
| `scratch.sql` | Learner scratchpad, run with `py q.py scratch.sql`. |
| `progress.json` | Live learner progress, written by `tutor.py`. Absent until the first run. |
