-- Portfolio 1: Relational schema for the University Student Result Portal
-- Engine: SQLite 3.31+ (generated columns required). Run: python3 build_db.py
PRAGMA foreign_keys = ON;

CREATE TABLE department (
    dept_id     INTEGER PRIMARY KEY,
    dept_name   TEXT NOT NULL UNIQUE,
    faculty     TEXT NOT NULL
);

CREATE TABLE programme (
    programme_id   INTEGER PRIMARY KEY,
    programme_name TEXT NOT NULL UNIQUE,
    award          TEXT NOT NULL CHECK (award IN ('BSc','MSc','PGD')),
    dept_id        INTEGER NOT NULL REFERENCES department(dept_id)
);

CREATE TABLE student (
    student_id   INTEGER PRIMARY KEY,
    matric_no    TEXT NOT NULL UNIQUE,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    email        TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
    programme_id INTEGER NOT NULL REFERENCES programme(programme_id),
    entry_year   INTEGER NOT NULL CHECK (entry_year BETWEEN 2015 AND 2026),
    status       TEXT NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active','graduated','withdrawn','suspended'))
);

CREATE TABLE lecturer (
    lecturer_id INTEGER PRIMARY KEY,
    staff_no    TEXT NOT NULL UNIQUE,
    full_name   TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    dept_id     INTEGER NOT NULL REFERENCES department(dept_id)
);

CREATE TABLE course (
    course_id    INTEGER PRIMARY KEY,
    course_code  TEXT NOT NULL UNIQUE,
    title        TEXT NOT NULL,
    credit_units INTEGER NOT NULL CHECK (credit_units BETWEEN 1 AND 6),
    level        INTEGER NOT NULL CHECK (level IN (100,200,300,400,500,800)),
    dept_id      INTEGER NOT NULL REFERENCES department(dept_id)
);

CREATE TABLE semester (
    semester_id INTEGER PRIMARY KEY,
    session     TEXT NOT NULL,                       -- e.g. 2024/2025
    term        TEXT NOT NULL CHECK (term IN ('First','Second')),
    UNIQUE (session, term)
);

CREATE TABLE course_offering (
    offering_id INTEGER PRIMARY KEY,
    course_id   INTEGER NOT NULL REFERENCES course(course_id),
    semester_id INTEGER NOT NULL REFERENCES semester(semester_id),
    lecturer_id INTEGER NOT NULL REFERENCES lecturer(lecturer_id),
    capacity    INTEGER NOT NULL CHECK (capacity > 0),
    seats_taken INTEGER NOT NULL DEFAULT 0,
    UNIQUE (course_id, semester_id),
    CHECK (seats_taken >= 0 AND seats_taken <= capacity)
);

CREATE TABLE registration (
    reg_id      INTEGER PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES student(student_id),
    offering_id INTEGER NOT NULL REFERENCES course_offering(offering_id),
    reg_date    TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (student_id, offering_id)          -- a student cannot register twice
);

CREATE TABLE result (
    reg_id      INTEGER PRIMARY KEY REFERENCES registration(reg_id) ON DELETE CASCADE,
    ca_score    INTEGER NOT NULL CHECK (ca_score   BETWEEN 0 AND 40),
    exam_score  INTEGER NOT NULL CHECK (exam_score BETWEEN 0 AND 60),
    total_score INTEGER GENERATED ALWAYS AS (ca_score + exam_score) VIRTUAL
);

-- Grade rules stored as data: removes the transitive dependency
-- total_score -> grade -> grade_point from the result table (3NF).
CREATE TABLE grade_scale (
    grade       TEXT PRIMARY KEY,
    min_score   INTEGER NOT NULL UNIQUE,
    max_score   INTEGER NOT NULL,
    grade_point INTEGER NOT NULL,
    CHECK (min_score <= max_score)
);

CREATE TABLE grade_audit (
    audit_id   INTEGER PRIMARY KEY,
    reg_id     INTEGER NOT NULL,
    old_total  INTEGER,
    new_total  INTEGER,
    changed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Every grade change is logged (supports the audit requirement)
CREATE TRIGGER trg_result_audit AFTER UPDATE ON result
BEGIN
    INSERT INTO grade_audit (reg_id, old_total, new_total)
    VALUES (OLD.reg_id, OLD.ca_score + OLD.exam_score, NEW.ca_score + NEW.exam_score);
END;

-- Graded results used by transcript / GPA queries
CREATE VIEW v_graded_result AS
SELECT r.reg_id, reg.student_id, o.semester_id, c.course_id, c.course_code,
       c.title, c.credit_units, r.total_score, g.grade, g.grade_point
FROM result r
JOIN registration reg    ON reg.reg_id = r.reg_id
JOIN course_offering o   ON o.offering_id = reg.offering_id
JOIN course c            ON c.course_id = o.course_id
JOIN grade_scale g       ON r.total_score BETWEEN g.min_score AND g.max_score;
