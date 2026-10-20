"""Portfolio 2: runs analytical queries, captures results + EXPLAIN QUERY PLAN,
then measures the effect of indexes. Writes everything under ./output/."""
import sqlite3, statistics, time, pathlib, textwrap
HERE = pathlib.Path(__file__).parent
OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
con = sqlite3.connect(HERE.parent / "university.db")
con.execute("PRAGMA foreign_keys=ON")

# ---------- Part A: business queries ----------
QUERIES = {
"Q1_transcript_student_1234": ("""
SELECT s.session, s.term, g.course_code, g.title, g.credit_units, g.total_score, g.grade, g.grade_point
FROM v_graded_result g
JOIN semester s ON s.semester_id = g.semester_id
WHERE g.student_id = 1234
ORDER BY s.session, s.term, g.course_code;""", ()),
"Q2_cgpa_student_1234": ("""
SELECT st.matric_no,
       SUM(g.credit_units) AS total_units,
       ROUND(1.0 * SUM(g.grade_point * g.credit_units) / SUM(g.credit_units), 2) AS cgpa
FROM v_graded_result g JOIN student st ON st.student_id = g.student_id
WHERE g.student_id = 1234
GROUP BY st.student_id;""", ()),
"Q3_top3_per_programme_by_cgpa": ("""
WITH cgpa AS (
  SELECT st.student_id, st.matric_no, st.programme_id,
         1.0 * SUM(g.grade_point * g.credit_units) / SUM(g.credit_units) AS cgpa
  FROM student st JOIN v_graded_result g ON g.student_id = st.student_id
  GROUP BY st.student_id),
ranked AS (
  SELECT *, RANK() OVER (PARTITION BY programme_id ORDER BY cgpa DESC) AS rnk FROM cgpa)
SELECT p.programme_name, r.matric_no, ROUND(r.cgpa,2) AS cgpa, r.rnk
FROM ranked r JOIN programme p ON p.programme_id = r.programme_id
WHERE r.rnk <= 3 ORDER BY p.programme_name, r.rnk, r.matric_no;""", ()),
"Q4_failure_rate_by_department": ("""
SELECT d.dept_name, COUNT(*) AS results,
       SUM(g.grade = 'F') AS fails,
       ROUND(100.0 * SUM(g.grade = 'F') / COUNT(*), 1) AS fail_pct
FROM v_graded_result g
JOIN course c ON c.course_id = g.course_id
JOIN department d ON d.dept_id = c.dept_id
GROUP BY d.dept_id ORDER BY fail_pct DESC;""", ()),
"Q5_class_list_offering_150": ("""
SELECT st.matric_no, st.first_name, st.last_name, r.ca_score, r.exam_score, r.total_score
FROM registration reg
JOIN student st ON st.student_id = reg.student_id
JOIN result r ON r.reg_id = reg.reg_id
WHERE reg.offering_id = 150
ORDER BY st.matric_no;""", ()),
}

with open(OUT/"queries_and_results.txt","w") as f:
    for name,(sql,args) in QUERIES.items():
        cur = con.execute(sql,args); cols=[d[0] for d in cur.description]; rows=cur.fetchall()
        f.write(f"=== {name} ===\n{sql.strip()}\n\n-- {len(rows)} row(s); first 8 shown\n")
        f.write(" | ".join(cols)+"\n")
        for r in rows[:8]: f.write(" | ".join(map(str,r))+"\n")
        f.write("\n")
        f.write("-- EXPLAIN QUERY PLAN\n")
        for p in con.execute("EXPLAIN QUERY PLAN "+sql,args): f.write(f"   {p[3]}\n")
        f.write("\n")

# ---------- Part B: indexing experiments ----------
TARGETS = {
"O1 class list for one offering": ("""SELECT st.matric_no, r.total_score FROM registration reg
 JOIN student st ON st.student_id=reg.student_id JOIN result r ON r.reg_id=reg.reg_id
 WHERE reg.offering_id = ?""", (150,),
 "CREATE INDEX idx_registration_offering ON registration(offering_id)"),
"O2 active students in a programme/intake": ("""SELECT COUNT(*) FROM student
 WHERE programme_id = ? AND status = 'active' AND entry_year = ?""", (3,2023),
 "CREATE INDEX idx_student_prog_status_year ON student(programme_id, status, entry_year)"),
"O3 failing results (score < 40)": ("""SELECT COUNT(*) FROM result WHERE total_score < ?""", (40,),
 "CREATE INDEX idx_result_total ON result(total_score)"),
"O4 results for one semester via offering": ("""SELECT COUNT(*) FROM registration reg
 JOIN course_offering o ON o.offering_id = reg.offering_id WHERE o.semester_id = ?""", (3,),
 "CREATE INDEX idx_offering_semester ON course_offering(semester_id)"),
}
def bench(sql,args,n=30):
    ts=[]
    for _ in range(n):
        t=time.perf_counter(); con.execute(sql,args).fetchall(); ts.append((time.perf_counter()-t)*1000)
    return statistics.median(ts)
def plan(sql,args): return [p[3] for p in con.execute("EXPLAIN QUERY PLAN "+sql,args)]

rows=[]; log=[]
for name,(sql,args,ddl) in TARGETS.items():
    con.execute("DROP INDEX IF EXISTS "+ddl.split()[2])
    con.execute("ANALYZE")
    before_plan, before_ms = plan(sql,args), bench(sql,args)
    con.execute(ddl); con.execute("ANALYZE")
    after_plan, after_ms = plan(sql,args), bench(sql,args)
    rows.append((name, before_ms, after_ms))
    log.append(f"### {name}\nSQL: {' '.join(sql.split())}\nIndex: {ddl}\n"
               f"BEFORE plan: {before_plan}\nAFTER  plan: {after_plan}\n"
               f"Median time: {before_ms:.3f} ms -> {after_ms:.3f} ms ({before_ms/after_ms:.1f}x)\n")
con.commit()
(OUT/"execution_plans_before_after.txt").write_text("\n".join(log))

# ---------- Part C: query rewrite (correlated subquery vs join) ----------
SLOW = """SELECT st.student_id,
 (SELECT COUNT(*) FROM registration r WHERE r.student_id = st.student_id) AS n
 FROM student st WHERE st.programme_id = 1"""
FAST = """SELECT st.student_id, COUNT(r.reg_id) AS n FROM student st
 LEFT JOIN registration r ON r.student_id = st.student_id
 WHERE st.programme_id = 1 GROUP BY st.student_id"""
a, b = bench(SLOW,(),10), bench(FAST,(),10)
same = sorted(con.execute(SLOW).fetchall())==sorted(con.execute(FAST).fetchall())

md = ["# Portfolio 2: Performance analysis (generated by run_portfolio2.py)\n",
      f"Dataset: {con.execute('select count(*) from registration').fetchone()[0]:,} registrations, "
      f"{con.execute('select count(*) from student').fetchone()[0]:,} students. Median of 30 runs, SQLite {sqlite3.sqlite_version}.\n",
      "| Experiment | Before (ms) | After (ms) | Speed-up |","|---|---:|---:|---:|"]
md += [f"| {n} | {b_:.3f} | {a_:.3f} | {b_/a_:.1f}x |" for n,b_,a_ in rows]
md += [f"\nQuery rewrite (correlated subquery vs LEFT JOIN + GROUP BY): {a:.2f} ms vs {b:.2f} ms; identical results: {same}.\n"]
(OUT/"performance_table.md").write_text("\n".join(md))
print("\n".join(md)); print(); print(*log, sep="\n")
