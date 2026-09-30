"""
Builds (or rebuilds) practice.db - the database you'll use for every lesson.
Run it any time to reset the data back to a known clean state:

    py setup_db.py
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "practice.db")

SCHEMA = """
DROP TABLE IF EXISTS employee_projects;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    dept_id   INTEGER PRIMARY KEY,
    dept_name TEXT    NOT NULL,
    location  TEXT    NOT NULL,
    budget    INTEGER NOT NULL
);

CREATE TABLE employees (
    emp_id     INTEGER PRIMARY KEY,
    first_name TEXT    NOT NULL,
    last_name  TEXT    NOT NULL,
    dept_id    INTEGER REFERENCES departments(dept_id),
    job_title  TEXT    NOT NULL,
    salary     INTEGER NOT NULL,
    hire_date  TEXT    NOT NULL,
    manager_id INTEGER REFERENCES employees(emp_id),
    email      TEXT    NOT NULL
);

CREATE TABLE projects (
    project_id   INTEGER PRIMARY KEY,
    project_name TEXT    NOT NULL,
    dept_id      INTEGER REFERENCES departments(dept_id),
    start_date   TEXT    NOT NULL,
    end_date     TEXT,               -- NULL means the project is still running
    budget       INTEGER NOT NULL
);

CREATE TABLE employee_projects (
    emp_id          INTEGER NOT NULL REFERENCES employees(emp_id),
    project_id      INTEGER NOT NULL REFERENCES projects(project_id),
    role            TEXT    NOT NULL,
    hours_allocated INTEGER NOT NULL,
    PRIMARY KEY (emp_id, project_id)
);
"""

DEPARTMENTS = [
    (1, "Engineering", "San Francisco", 2000000),
    (2, "Sales",       "New York",      1500000),
    (3, "Marketing",   "New York",       800000),
    (4, "HR",          "Chicago",        400000),
]

EMPLOYEES = [
    # emp_id, first, last, dept_id, job_title, salary, hire_date, manager_id, email
    (1,  "Alice",  "Johnson",  1, "Engineering Manager", 165000, "2018-03-15", None, "alice.johnson@example.com"),
    (2,  "Bob",    "Smith",    1, "Senior Engineer",     135000, "2019-07-01", 1,    "bob.smith@example.com"),
    (3,  "Carol",  "Williams", 1, "Engineer",            110000, "2020-01-20", 1,    "carol.williams@example.com"),
    (4,  "David",  "Brown",    1, "Engineer",            105000, "2021-06-10", 1,    "david.brown@example.com"),
    (5,  "Eve",    "Davis",    1, "Junior Engineer",      85000, "2022-09-05", 2,    "eve.davis@example.com"),
    (6,  "Frank",  "Miller",   2, "Sales Manager",       145000, "2017-11-30", None, "frank.miller@example.com"),
    (7,  "Grace",  "Wilson",   2, "Account Executive",    95000, "2019-02-14", 6,    "grace.wilson@example.com"),
    (8,  "Henry",  "Moore",    2, "Account Executive",    92000, "2020-08-19", 6,    "henry.moore@example.com"),
    (9,  "Ivy",    "Taylor",   2, "Sales Rep",            70000, "2023-01-09", 6,    "ivy.taylor@example.com"),
    (10, "Jack",   "Anderson", 3, "Marketing Manager",   130000, "2018-05-22", None, "jack.anderson@example.com"),
    (11, "Karen",  "Thomas",   3, "Content Strategist",   88000, "2021-03-30", 10,   "karen.thomas@example.com"),
    (12, "Leo",    "Jackson",  3, "SEO Specialist",       82000, "2022-11-15", 10,   "leo.jackson@example.com"),
    (13, "Mia",    "White",    4, "HR Manager",          120000, "2019-09-01", None, "mia.white@example.com"),
    (14, "Nina",   "Harris",   4, "Recruiter",            75000, "2021-07-12", 13,   "nina.harris@example.com"),
    (15, "Oscar",  "Martin",   1, "Engineer",            108000, "2023-04-03", 1,    "oscar.martin@example.com"),
    (16, "Paula",  "Clark", None, "Consultant",          100000, "2024-02-01", None, "paula.clark@example.com"),
]

PROJECTS = [
    # project_id, project_name, dept_id, start_date, end_date, budget
    (1, "Apollo",  1, "2022-01-01", "2022-12-31", 500000),
    (2, "Boreas",  1, "2023-03-01", None,         750000),
    (3, "Cronus",  2, "2023-06-01", None,         300000),
    (4, "Demeter", 3, "2022-09-01", "2023-03-31", 200000),
    (5, "Eos",     1, "2024-01-15", None,         400000),
    (6, "Helios",  2, "2021-05-01", "2021-11-30", 150000),
]

EMPLOYEE_PROJECTS = [
    # emp_id, project_id, role, hours_allocated
    (1,  1, "Lead",            200),
    (2,  1, "Developer",       400),
    (3,  1, "Developer",       400),
    (2,  2, "Lead",            300),
    (4,  2, "Developer",       500),
    (5,  2, "Developer",       500),
    (3,  5, "Lead",            350),
    (15, 5, "Developer",       450),
    (1,  5, "Advisor",         100),
    (6,  3, "Lead",            250),
    (7,  3, "Account Manager", 300),
    (8,  3, "Support",         200),
    (10, 4, "Lead",            200),
    (11, 4, "Contributor",     350),
    (12, 4, "Contributor",     300),
    (6,  6, "Lead",            220),
    (7,  6, "Contributor",     260),
]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)", DEPARTMENTS)
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", EMPLOYEES)
    conn.executemany("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?)", PROJECTS)
    conn.executemany("INSERT INTO employee_projects VALUES (?, ?, ?, ?)", EMPLOYEE_PROJECTS)
    conn.commit()

    counts = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("departments", "employees", "projects", "employee_projects")
    }
    conn.close()
    print(f"Built {DB_PATH}")
    for t, n in counts.items():
        print(f"  {t:18} {n:3} rows")


if __name__ == "__main__":
    main()
