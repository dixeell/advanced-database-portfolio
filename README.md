# MIT 8103 Advanced Database Systems: Portfolio

**Student:** <Sadiq Muhammad> | **Matric No:** <2026/A/MIT/0731> | **Session:** 2026/2027, First Semester

## Selected case study (stated per Section 2 of the brief)

| Item | Statement |
|---|---|
| Organisation / scenario | **Northgate University Student Result Portal**, a *simulated* university (synthetic data, no real students) |
| Nature of the system | Academic records: departments, programmes, courses, semester offerings, registration and result processing |
| Users of the database | Students (view transcript/CGPA), lecturers (enter scores), exams officers (audit, reports), registry/admin |
| Major data stored | Students, programmes, departments, lecturers, courses, semesters, course offerings, registrations, CA/exam scores, grade scale, grade audit log |
| Key operations | Register courses, enter/correct grades, compute GPA/CGPA, generate transcripts, rank students, audit grade changes |

All five portfolios use this same case study and the same dataset (2,000 students, 40,000 registrations/results).

## How to reproduce (needs only Python 3.9+ and `matplotlib`; SQLite ships with Python)

```bash
python3 portfolio-1-database-design/build_db.py        # creates university.db
python3 portfolio-1-database-design/er_diagram.py      # redraws the ER diagram
python3 portfolio-2-query-optimisation/run_portfolio2.py
python3 portfolio-3-transactions-concurrency/run_portfolio3.py
python3 portfolio-4-nosql/run_portfolio4.py
python3 portfolio-5-distributed-cloud/simulate_distribution.py
```

Each folder has its own README explaining what was implemented, how it was tested, and what the output shows.

## Portfolio map

| Portfolio | Folder | Main evidence |
|---|---|---|
| 1 Database design | `portfolio-1-database-design/` | `schema.sql`, `er_diagram.png`, `normalisation.md` |
| 2 Query optimisation | `portfolio-2-query-optimisation/` | `output/` query results, plans before/after, `PERFORMANCE_ANALYSIS.md` |
| 3 Transactions | `portfolio-3-transactions-concurrency/` | `output/transaction_log.txt`, `postgres_isolation_levels.sql` |
| 4 NoSQL | `portfolio-4-nosql/` | document model, `mongodb_queries.js`, SQL cross-check |
| 5 Distributed/cloud | `portfolio-5-distributed-cloud/` | `DISCUSSION.md`, simulation output, `docker-compose.yml` |

## What was verified and what was not
Scripts in Python/SQLite were run and their outputs are saved in each `output/` folder. Files marked **UNTESTED** (`postgres_isolation_levels.sql`, `mongodb_queries.js`, `docker-compose.yml`) need a PostgreSQL/MongoDB/Docker environment; run them and add your own screenshots to the matching `evidence/` folder.

## AI Use Declaration
See `AI_USE_DECLARATION.md`.
