"""Portfolio 4: builds a MongoDB-style DOCUMENT model from the relational data.
One document per student embeds their registrations + results (read-optimised for
transcripts). Output: output/students.json (JSON Lines, ready for mongoimport)."""
import sqlite3, json, pathlib
HERE = pathlib.Path(__file__).parent; OUT = HERE/"output"; OUT.mkdir(exist_ok=True)
con = sqlite3.connect(HERE.parent/"university.db"); con.row_factory = sqlite3.Row
prog = {r["programme_id"]: dict(r) for r in con.execute(
    "SELECT p.programme_id, p.programme_name, p.award, d.dept_name FROM programme p JOIN department d USING(dept_id)")}
sem = {r["semester_id"]: f'{r["session"]} {r["term"]}' for r in con.execute("SELECT * FROM semester")}
by_student = {}
for r in con.execute("SELECT * FROM v_graded_result"):
    by_student.setdefault(r["student_id"], []).append({
        "course_code": r["course_code"], "title": r["title"], "units": r["credit_units"],
        "semester": sem[r["semester_id"]], "score": r["total_score"], "grade": r["grade"], "gp": r["grade_point"]})
n = 0
with open(OUT/"students.json","w") as f:
    for s in con.execute("SELECT * FROM student ORDER BY student_id"):
        res = by_student.get(s["student_id"], [])
        units = sum(x["units"] for x in res)
        doc = {"_id": s["matric_no"], "name": {"first": s["first_name"], "last": s["last_name"]},
               "email": s["email"], "entryYear": s["entry_year"], "status": s["status"],
               "programme": {"name": prog[s["programme_id"]]["programme_name"],
                             "award": prog[s["programme_id"]]["award"], "department": prog[s["programme_id"]]["dept_name"]},
               "results": res,                                  # embedded (bounded: ~20 per semester set)
               "cgpa": round(sum(x["gp"]*x["units"] for x in res)/units, 2) if units else None}   # pre-computed
        f.write(json.dumps(doc)+"\n"); n += 1
print(n, "documents written")
