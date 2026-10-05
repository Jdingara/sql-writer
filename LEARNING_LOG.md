# Sasi's SQL Learning Log

A running record of every practice session — every question, Sasi's answer, the
mistakes, and what was learned — plus an honest read on how far along the path to
"job-market SQL" Sasi is. Claude updates this at the end of each session.

[PROJECT_STATUS.md](PROJECT_STATUS.md) is the project's full context; this file
is just the learning record and report card.

---

## How "market-ready" is measured

Three bands. Sasi's target is the middle one.

| Band | What it means | Typical roles | In scope? |
|------|---------------|---------------|-----------|
| **A — SQL-literate** | Reads queries others wrote, runs them, sanity-checks the numbers, knows what tables/columns exist | any technical-adjacent role: PM, ops, support, functional/ERP consultant | foundation |
| **B — Writes day-to-day SQL** | Writes own `SELECT` + `WHERE` + `JOIN` + `GROUP BY` + aggregates, unaided, to pull and verify data | data/ops analyst, implementation consultant, technical support engineer, technical PM | **← THE TARGET** |
| **C — SQL developer / DBA** | Schema design, indexing, query optimization, stored procedures, DB administration | SQL developer, database engineer, DBA | out of scope (agreed) |

Solid **Band B** = "I can manage the work without a developer running every query
for me." That's roughly Lessons 2–8 of this course, done fluently and unaided.

---

## Market-readiness snapshot

**2026-10-05 — Session 6 (Lesson 7, JOIN): 77/100. Full target coverage except Lesson 8.**

- 5 of 6 JOIN questions first try, plus one correct-result query that used double
  quotes for a string (SQLite tolerates it; real databases don't — flagged).
- Checked the schema before writing the join (asked "there's no `dept_name` in
  employees?") and then wrote the query cleanly — the schema-first habit is
  paying off.
- Grasped the core model fast: a join glues rows where keys match, only matched
  rows survive, and aliases (`e.`, `d.`) are needed once two tables share a
  column name like `dept_id`.
- JOIN + `GROUP BY` combined correctly (Q5) — grouping by a *name* pulled through
  the join instead of a raw id.
- Coverage 62 → 75. Only **Lesson 8 (LEFT JOIN / anti-joins — "find the people
  with no X")** remains to fully cover the target level.

**2026-09-23 — Session 5 (Lesson 6, GROUP BY/HAVING): 70/100.**

- 5 of 7 correct first try; every query that got written was clean. The two
  misses were the two classic first-time `GROUP BY` confusions: thinking it
  *sorts* rather than *collapses* rows (Q1), and trying to filter an aggregate
  with `WHERE` / inside the `SELECT` list instead of `HAVING` (Q5, self-corrected
  after explanation). Both are near-universal beginner trips on this topic, not a
  red flag.
- Comfortable with: aggregate-per-group (`COUNT`/`AVG`/`MAX` `... GROUP BY`),
  grouping on text columns, combining `GROUP BY` with `ORDER BY` and with an
  alias, and reading "no group for a value with zero rows" (HR had no projects →
  simply absent, not a zero row).
- Coverage jumps to 62 — this was the last conceptually new/hard topic besides
  `JOIN`. Only Lessons 7–8 (`JOIN`) remain for full target coverage.

**2026-09-10 — Session 4 (Lesson 5, aggregates): 65/100. Solidly in Band B.**

- Cleanest lesson so far — `COUNT` / `SUM` / `AVG` / `MIN` / `MAX`, aggregate +
  `WHERE`, aggregate + `AS` alias, all essentially first try, zero syntax errors.
- **The NULL idea landed.** Opened with a NULL re-drill (answered correctly), and
  on the `COUNT(manager_id)` question predicted 11 *and explained it unaided* —
  "11 have a manager, 5 are NULL so they don't count." Concept now transferring
  to new contexts, not just memorised for one question.
- Coverage 42 → 52. Remaining gap to "fully job-ready": `GROUP BY` (Lesson 6) and
  `JOIN` (Lessons 7–8) — JOIN is the one that unlocks cross-table questions.

**2026-09-09 — Session 3 (Lesson 4, NULL): 57/100. Crossed into Band B.**

- Every **query** in Lesson 4 was correct first try, no syntax errors — including
  `COALESCE(manager_id, 0) AS manager_or_zero`. The mechanics (`IS NULL`,
  `IS NOT NULL`, `COALESCE`) are solid.
- Both **concept / multiple-choice** questions were missed, though: picked
  `= NULL` over `IS NULL` right after being told the rule (Q1), and misread `<>`
  while reasoning about why NULL rows vanish from a filter (Q5). The
  three-valued-logic idea (NULL comparisons are UNKNOWN, and `WHERE` keeps only
  TRUE) has not fully stuck — revisit it.
- Score crosses 55 → technically **Band B ("writes day-to-day SQL")**, but this
  is the *entry* of that band. The big practical pieces — aggregates, `GROUP BY`,
  and especially `JOIN` — are still ahead (Lessons 5–8). Coverage only 42/100.

**2026-09-04 — Session 2 (Lessons 2–3): 52/100. Closing in on Band B.**

- Lesson 3 (`ORDER BY` / `LIMIT` / `DISTINCT`) was the cleanest lesson yet — 6 of
  7 correct on the first try, including the harder multi-key sort
  (`ORDER BY dept_id, salary DESC`). Only miss: forgot `DESC` once (got oldest
  hires instead of newest) — self-corrected in one nudge.
- Can now **filter** (`WHERE`, `AND`/`OR`, `BETWEEN`, `IN`, `LIKE`) **and arrange**
  (`ORDER BY`, `LIMIT`, `DISTINCT`) data — that combination covers a large slice
  of real "pull me a list of X" requests.
- The trailing-`s` table-name typo from Session 1 stayed **gone**.
- Watch-item from earlier this session, incomplete queries (missing a column /
  condition), didn't recur in Lesson 3 — provisionally improving, keep an eye on it.
- Distance to target (Band B ≈ 55–60): very close. Lessons 4 (NULL), 5–6
  (aggregates, GROUP BY) and 7–8 (JOIN) remain — JOIN is the big one left.

**2026-09-03 — Session 1: 30/100. Getting started.**

- Could write a single-table `SELECT` with columns and an `AS` alias when the
  `SELECT … FROM` shape was prompted. No filtering yet.
- Every mistake was a typo, not a misunderstanding — table names missing `s`,
  `''` vs `' '`, English-instead-of-SQL once.

---

## Sessions

### Session 1 — 2026-09-03

**Lesson:** 1 — SELECT, FROM, columns, aliases, expressions
**Tool:** started in the terminal (`tutor.py`); switched mid-session to DBeaver +
chat grading, because the terminal's exact-match grading was punishing typos
rather than testing understanding.

**Questions & answers:**

| Q | Asked | What Sasi wrote | Outcome |
|---|-------|-----------------|---------|
| 1 | Which keyword names the table? | understood it as `FROM` | ✅ concept correct |
| 2 | `project_name`, `budget` of every project | `select project)name, budget FROM project`, then `… from project` | ❌ ×2 typos: `)` for `_`, `project` for `projects`. Then in DBeaver: `select project_name, budget from projects` → ✅ 6 rows |
| 3 | Every column of `departments` | `select * from departments;` | ✅ correct — `*` = all columns |
| 4 | `first_name` as `given_name`, plus `last_name` | terminal: `select employees show first_name and last_name` (wrote English). DBeaver: `select first_name AS given_name, last_name from employees` | ❌ then ✅ 16 rows |
| 5 | `dept_name`, `budget / 1000` as `budget_in_thousands` | terminal: `select dept_name , ((budget_in_thousands=1000)/1000) from departments`. DBeaver: `select dept_name, budget / 1000 AS budget_in_thousands from departments` | ❌ then ✅ 4 rows — first clean try in DBeaver |
| 6 | `full_name` = first name + space + last name | terminal: `select first_name || '' || last_name from employee` ("no idea" first). DBeaver: `select first_name ||' '|| last_name AS full_name from employees` | ❌ then ✅ 16 rows — clean, first try in DBeaver |

**Lesson 1: complete — all 6 correct in DBeaver.**

**Mistake patterns (most frequent first):**

1. **Table name missing the trailing `s`** — `project`, `employee`, once
   `departsment`. The #1 error this session. Fix in play: DBeaver's left panel
   lists exact names; all 4 tables are plural
   (`departments`, `employees`, `projects`, `employee_projects`).
2. **Writing the question as an English sentence** instead of SQL
   (`select employees show first_name and last_name`). Fix: always start from
   `SELECT <columns> FROM <table>`; columns are separated by commas, never the
   word "and".
3. **Computed / aliased columns** — assuming the new name already exists; using
   `=` to "assign" it. Fix: `<calculation> AS <new_name>`. `AS` names things,
   `=` compares things.
4. **A space is a string** — `''` is empty, `' '` is a single space.
5. **Key slips** — `)` typed instead of `_`.

**What clicked this session:**

- The `SELECT … FROM …` skeleton — producing clean, correct queries in DBeaver
  (Q2, Q3, Q4 all correct once off the terminal).
- `AS` for renaming a column — Q4 went from a full English sentence to a correct
  query.
- `*` means every column.
- Changing tools (DBeaver GUI) removed the single biggest source of errors.

---

### Session 2 — 2026-09-04

**Lesson:** 2 — `WHERE` (filtering rows). **Tool:** DBeaver + chat grading.

**Questions & answers:**

| Q | Asked | What Sasi wrote | Outcome |
|---|-------|-----------------|---------|
| 1 | Which clause keeps only `salary > 100000`? | `a` (`WHERE salary > 100000`) | ✅ first try |
| 2 | `first_name, last_name, salary` where salary ≥ 100000 | `select first_name, Last_name from employees where salary >= 100000` | ⚠️ filter right (9 rows), but **left out the `salary` column** → added it → ✅ |
| 3 | `emp_id, first_name, job_title` for dept 1 | `... from departments where dept_id = 1` | ❌ wrong table — those columns are in `employees`, not `departments` → fixed → ✅ 6 rows |
| 4 | `first_name, last_name` hired before 2020-01-01 | `... where hire_date < '2020-01-01'` | ✅ first try (after inspecting the data format) |
| 5 | Engineers earning > 106000 | `... where job_title = 'Engineer'` | ⚠️ **forgot the second condition** `AND salary > 106000` → added it → ✅ 2 rows |
| 6 | `project_name`, budget 200000–500000 | `where budget between 200000 and 500000;` | ❌ **fragment — no `SELECT … FROM`** → added front → ✅ 4 rows |
| 7 | Sales + Marketing employees, use `IN` | `... where dept IN (1,2)` | ❌ `dept` → `dept_id`; `(1,2)` → `(2,3)` → fixed → ✅ 7 rows |
| 8 | `first_name, last_name, email` where last name starts M | `... where last_name LIKE 'M%'` | ✅ first try, clean |

**Lesson 2: complete — all 8 correct.**

**Mistake patterns (most frequent first):**

1. **Incomplete queries** — a fragment (Q6, no `SELECT…FROM`), a missing column
   the question named (Q2), a missing second condition (Q5). New #1 issue. Fix:
   write the whole `SELECT <cols> FROM <table> WHERE <conditions>` skeleton every
   time, then re-read the question and tick off every column and every condition
   it mentions.
2. **Wrong table** (Q3) — reached for `departments` because the question said
   "department"; the columns actually live in `employees`. Fix: pick the table by
   *which table has the columns you need* (check the left panel), not by a word
   in the question.
3. **Trailing `s` on table names** — the Session 1 #1 issue: **zero times this
   session.** Keep the schema-panel habit.

**What clicked this session:**

- `WHERE` and all its operators — `=`, `>`, `<`, `>=`, `<=`, `AND`, `OR`,
  `BETWEEN … AND …`, `IN (…)`, `LIKE 'M%'`.
- `>=` vs `>` — saw Paula (exactly 100000) stay in for `>=` and understood why.
- `BETWEEN … AND …` is one phrase; its `AND` is a separator, not a second
  condition.
- `IN (2, 3)` = "dept 2 **or** 3"; each row still has one value — the result is
  two groups stacked.
- Started using the schema panel and the Data tab to inspect tables directly.

**Lesson 3 — ORDER BY / LIMIT / DISTINCT** (same session, continued straight on)

| Q | Asked | What Sasi wrote | Outcome |
|---|-------|-----------------|---------|
| 1 | What does `ORDER BY salary DESC` do? | `b` | ✅ first try |
| 2 | All employees, highest salary first | `... order by salary desc;` | ✅ first try, clean, 16 rows |
| 3 | Top 3 highest-paid | `... order by salary desc limit 3;` | ✅ first try, clean |
| 4 | Distinct department locations | `select distinct location from departments;` | ✅ first try, clean, 3 rows |
| 5 | Distinct `dept_id` in `projects` | `select distinct dept_id from projects;` | ✅ first try, clean, 3 rows |
| 6 | 5 most recently hired, newest first | `... order by hire_date limit 5;` | ❌ **missing `DESC`** — got the 5 *oldest* hires instead → added `desc` → ✅ |
| 7 | Sort by `dept_id` asc, then `salary` desc within dept | `... order by dept_id, salary desc;` | ✅ first try, clean, 16 rows — correctly put NULL-dept Paula first |

**Lesson 3: complete — 6 of 7 correct first try; the one miss fixed in one nudge.**

**Mistake pattern added:**

4. **Forgot `DESC`.** Without it, `ORDER BY` defaults to ascending — got oldest
   instead of newest. Fix: read "newest/highest/most first" as a `DESC` cue.

**What clicked in Lesson 3:**

- `ORDER BY` (+ `DESC`), `LIMIT` after the sort, `DISTINCT` for unique values —
  all landed fast, mostly first-try.
- Multi-column `ORDER BY` (`dept_id, salary DESC`) — first key sorts, second key
  breaks ties, each with its own direction. Got this **first try**, no errors —
  the most advanced thing done so far.
- Saw `NULL` sort first in ascending order (Paula, no department, at the very
  top) — sets up Lesson 4.

---

### Session 3 — 2026-09-09

**Lesson:** 4 — `NULL` (`IS NULL`, `IS NOT NULL`, `COALESCE`). **Tool:** DBeaver +
chat grading. (Started 2026-09-04, finished 2026-09-09 after a gap.)

| Q | Asked | What Sasi wrote | Outcome |
|---|-------|-----------------|---------|
| 1 | Which finds employees with no manager? | `a` (`WHERE manager_id = NULL`) | ❌ answer is `b` (`IS NULL`) — chose `= NULL` right after the rule was given |
| 2 | `first_name, last_name` where no manager | `... where manager_id is null;` | ✅ first try, clean, 5 rows |
| 3 | `project_name` of still-running projects | `... where end_date is null;` | ✅ first try, clean, 3 rows |
| 4 | Employees who have a department | `... where dept_id is not null;` | ✅ first try, clean, 15 rows |
| 5 | Why does `COUNT(*) WHERE end_date <> '2022-12-31'` give 2, not 5? | proposed own option: "only 2 projects' end_date equals that date" | ❌ misread `<>` as "equals"; answer is `b` (NULL comparisons are UNKNOWN, `WHERE` drops them) |
| 6 | `first_name, last_name, COALESCE(manager_id, 0) AS manager_or_zero` | exactly that | ✅ first try, clean, 16 rows |

**Lesson 4: complete — all 4 query questions correct first try; both concept /
MCQ questions missed.**

**Mistake patterns this session:**

5. **NULL three-valued logic not stuck.** Twice reasoned about NULL as if a
   comparison returns TRUE/FALSE. It returns **UNKNOWN**, and `WHERE` keeps only
   TRUE — so `= NULL` never matches, and `<> 'x'` silently drops NULL rows. Drill:
   "to test a missing value it's *always* `IS NULL` / `IS NOT NULL`"; "a filter on
   a column that can be NULL needs `OR col IS NULL` if you want those rows."
6. **Misreading the operator** — read `<>` ("not equal") as "equal" in Q5.

**What clicked:**

- Writing NULL queries: `IS NULL`, `IS NOT NULL`, and `COALESCE(col, fallback)`
  all correct first try, no syntax slips.
- The *demo* in Q5's explanation (the 6-row table showing which rows are TRUE /
  FALSE / UNKNOWN) seemed to land better than the abstract rule.

---

### Session 4 — 2026-09-10

**Lesson:** 5 — aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
**Tool:** DBeaver + chat grading. Opened with a NULL re-drill.

| Q | Asked | What Sasi did | Outcome |
|---|-------|---------------|---------|
| 0 | NULL re-drill: which clause excludes a date *and* keeps NULLs? | `b` (`<> 'x' OR end_date IS NULL`) | ✅ — NULL rule now correct |
| 1 | Which function counts rows? | thought aloud, tangled on the word "match", but stated `COUNT(*)` vs `COUNT(col)` correctly | ✅ concept (my wording was loose) |
| 2 | How many employees | `select count(*) from employees;` | ✅ first try → 16 |
| 3 | Total of all salaries | `select sum(salary) from employees;` | ✅ first try → 1,705,000 |
| 4 | Average salary | `select avg(salary) from employees;` | ✅ first try → 106,562.5 |
| 5 | Highest and lowest salary in one query | `select max(salary), min(salary) from employees;` | ✅ first try → 165,000 / 70,000 |
| 6 | Count of Engineering employees | `select count(*) from employees where dept_id = 1;` | ✅ first try → 6 |
| 7 | Predict `COUNT(manager_id)` (16 rows, 5 NULL) | predicted **11**, explained: "11 have a manager, 5 are NULL so not counted" | ✅ **correct prediction + unaided reasoning** |
| 8 | Avg Sales salary, column `avg_sales_salary` | `select avg(salary) as avg_sales_salary from employees where dept_id = 2;` | ✅ first try → 100,500 |

**Lesson 5: complete — every question essentially first try, no syntax errors.**

**What clicked:**

- All five aggregates, plus aggregate + `WHERE` and aggregate + `AS`.
- `COUNT(*)` vs `COUNT(column)` — and used the `COUNT(*) − COUNT(col)` gap as a
  way to measure how many NULLs a column has.
- NULL three-valued logic is now transferring: correct on the re-drill and on a
  fresh aggregate context, with self-generated reasoning.

**No new mistake patterns.** Prior watch-items (table-name `s`, incomplete
queries, NULL logic) all holding / resolved.

---

### Session 5 — 2026-09-23

**Lesson:** 6 — `GROUP BY` (+ `HAVING`). **Tool:** DBeaver + chat grading.
(Gap since last session: ~2 weeks.)

| Q | Asked | What Sasi did | Outcome |
|---|-------|---------------|---------|
| 1 | What does `GROUP BY dept_id` do? | `a` ("sorts rows") | ❌ answer is `c` (collapses into one row per group) — the classic GROUP BY-vs-ORDER BY mix-up |
| 2 | Employee count per department | `select dept_id, count(*) from employees group by dept_id;` | ✅ first try → 5 rows, sums to 16 |
| 3 | Avg salary per department, alias `avg_salary` | `select dept_id, avg(salary) as avg_salary from employees group by dept_id;` | ✅ first try → 5 rows |
| 4 | Count per `job_title`, biggest first | `select job_title, count(*) from employees group by job_title order by count(*) desc;` | ✅ first try → Engineer 3, Account Executive 2, rest 1 |
| 5 | Departments with more than 3 employees | attempt 1: `count(*) > 3` in the SELECT list + `count(*) is not null` after GROUP BY (no `HAVING`) — ran, but wrong (0/1 column, all 5 groups). attempt 2 (following the explanation): `... group by dept_id having count(*) > 3;` | ❌ then ✅ 2 rows (dept 1, dept 2) |
| 6 | Highest salary per department, alias `top_salary`, sorted | `select dept_id, max(salary) as top_salary from employees group by dept_id order by dept_id;` | ✅ first try → 5 rows |
| 7 | Project count per department (different table) | `select dept_id, count(*) from projects group by dept_id;` | ✅ first try → 3 rows, HR correctly absent |

**Lesson 6: complete — 5 of 7 correct first try; the 2 misses were the two
classic first-time `GROUP BY`/`HAVING` confusions, not carelessness.**

**Mistake patterns this session (both topic-specific, expected on a first
`GROUP BY` lesson):**

7. **`GROUP BY` confused with `ORDER BY`** — thought it sorts rather than
   collapses rows into one-row-per-group.
8. **Tried to filter an aggregate with `WHERE` / inside the `SELECT` list**
   instead of `HAVING`. Rule: `WHERE` filters rows *before* grouping; `HAVING`
   filters groups *after*. An aggregate condition can only go in `HAVING`.

**What clicked:**

- Aggregate-per-group is solid: `COUNT`, `AVG`, `MAX`, each `... GROUP BY col`,
  with an alias and with `ORDER BY` — all clean.
- Grouping works the same on a text column (`job_title`) as a number (`dept_id`).
- Read "3 rows, not 4" correctly for Q7 — understood that a department with zero
  matching rows gets **no group at all**, not a zero-count row.
- Diagnosed their own wrong Q5 attempt correctly once shown the fix (recognised
  the 0/1 column wasn't what was wanted).

**For next session:**

- **Lessons 7–8** — `JOIN`: combining rows from two tables (e.g. employee name
  *with* department name, not just `dept_id`). Last big piece for full coverage
  of the target level.
- No re-drill needed on `GROUP BY`/`HAVING` — the misses were first-exposure,
  not a stuck pattern; revisit only if it recurs.

---

### Session 6 — 2026-09-23 → 2026-10-05

**Lesson:** 7 — `JOIN` (two-table joins). **Tool:** DBeaver + chat grading.
Paused mid-lesson for a git/GitHub checkpoint (repo pushed to
github.com/Jdingara/sql-writer on 2026-10-01); resumed and finished 2026-10-05.

| Q | Asked | What Sasi did | Outcome |
|---|-------|---------------|---------|
| 1 | What does `JOIN` fundamentally do? | `a` (combines two tables, matching rows where a shared column is equal) | ✅ first try |
| 2 | Each employee's name + department name | checked first ("there is no `dept_name` in employees?") → then `select e.first_name, e.last_name, d.dept_name from employees e join departments d on e.dept_id = d.dept_id;` | ✅ 15 rows; Paula correctly absent |
| 3 | Each project's name + owning department name | `select p.project_name, d.dept_name from projects p join departments d on p.dept_id = d.dept_id;` | ✅ first try → 6 rows |
| 4 | Engineering employees + department location, salary shown | `... where d.dept_name = "Engineering";` | ✅ correct result, but **double quotes** on a string — SQLite-only leniency, flagged; should be `'Engineering'` |
| 5 | Avg salary per department name (JOIN + GROUP BY) | `select d.dept_name, avg(e.salary) as avg_salary ... group by d.dept_name;` | ✅ first try → 4 rows |
| 6 | Who works on which project, with role | `select e.first_name, e.last_name, ep.project_id, ep.role from employees e join employee_projects ep on e.emp_id = ep.emp_id;` | ✅ first try → 17 rows; Bob/Carol/Alice appear more than once (multi-project) |

**Lesson 7: complete — 5 of 6 clean first try; 1 correct result with a quoting
habit to fix.**

**Mistake patterns this session:**

9. **Double quotes around a text value** (Q4). Worked in SQLite because of its
   leniency, but double quotes mean identifiers in standard SQL and most real
   databases. Rule: text values always in **single** quotes (`'Engineering'`).

**What clicked:**

- The JOIN model: glue rows where keys match; unmatched rows drop out (Paula has
  no department, so she disappears from any department join).
- Table aliases (`e.`, `d.`, `ep.`) — needed once two tables share a column name
  like `dept_id`. Used them correctly from Q2 onward.
- `WHERE` on a joined table's column; `GROUP BY` on a joined table's column
  (Q4 and Q5).
- Checked the schema before writing the join rather than guessing a column name.

**For next session:**

- **Lesson 8** — `LEFT JOIN` and anti-joins ("people with **no** project", "departments
  with **no** employees"). Last lesson for full target coverage.
- Keep: single quotes for every text value; check the schema when unsure which
  table holds a column.
