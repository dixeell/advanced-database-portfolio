# MIT 8103 Advanced Database Systems: Portfolio

**Student:** Sadiq Muhammad | **Matric No:** 2026/A/MIT/0731 | **Session:** 2026/2027, First Semester

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
python portfolio-1-database-design/build_db.py        # creates university.db
python portfolio-1-database-design/er_diagram.py      # redraws the ER diagram
python portfolio-2-query-optimisation/run_portfolio2.py
python portfolio-3-transactions-concurrency/run_portfolio3.py
python portfolio-4-nosql/run_portfolio4.py
python portfolio-5-distributed-cloud/simulate_distribution.py
```

Each folder has its own README explaining what was implemented, how it was tested, and what the output shows.

## Portfolio map

| Portfolio | Folder | Main evidence |
|---|---|---|
| 1 Database design | `portfolio-1-database-design/` | `schema.sql`, `er_diagram.png`, `normalisation.md`, `evidence/` |
| 2 Query optimisation | `portfolio-2-query-optimisation/` | `output/` query results, plans before/after, `PERFORMANCE_ANALYSIS.md`, `evidence/` |
| 3 Transactions | `portfolio-3-transactions-concurrency/` | `output/transaction_log.txt`, PostgreSQL isolation demo, `evidence/` |
| 4 NoSQL | `portfolio-4-nosql/` | document model, MongoDB queries, SQL cross-check, `evidence/` |
| 5 Distributed/cloud | `portfolio-5-distributed-cloud/` | `DISCUSSION.md`, simulation output, MongoDB Atlas replica set screenshots in `evidence/` |

## What was verified
- The Python/SQLite scripts were run and their outputs are saved in each `output/` folder.
- Portfolio 3: I ran the PostgreSQL isolation demonstration (READ COMMITTED, REPEATABLE READ and `FOR UPDATE` locking) in two psql sessions.
- Portfolio 4: I imported the document model into MongoDB and ran the queries in mongosh. The results matched the SQL results.
- Portfolio 5: I deployed the same data to a free MongoDB Atlas cluster (a replica set with one primary and two secondaries).
- Screenshots of all of this are in each portfolio's `evidence/` folder.
- `docker-compose.yml` was not used for deployment; it is left in the repository as a design reference only.

## AI Use Declaration
See `AI_USE_DECLARATION.md`.