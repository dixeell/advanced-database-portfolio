"""Runs the document-model queries in pure Python (same logic as the MongoDB
aggregation pipelines in mongodb_queries.js) and cross-checks them against SQL."""
import json, sqlite3, pathlib, collections, subprocess, sys
HERE = pathlib.Path(__file__).parent
subprocess.run([sys.executable, HERE/"export_to_documents.py"], check=True)
docs = [json.loads(l) for l in open(HERE/"output"/"students.json")]
con = sqlite3.connect(HERE.parent/"university.db")
log = open(HERE/"output"/"nosql_results.txt","w")
def say(*a):
    s=" ".join(map(str,a)); print(s); log.write(s+"\n")

say("--- Q1 transcript lookup by _id (db.students.findOne({_id: ...})) ---")
d = docs[1233]; say(d["_id"], d["name"], "| results embedded:", len(d["results"]), "| cgpa:", d["cgpa"])
say("first result:", d["results"][0])

say("\n--- Q2 average CGPA per programme (aggregation: $group by programme.name, $avg cgpa) ---")
g = collections.defaultdict(list)
for x in docs:
    if x["cgpa"] is not None: g[x["programme"]["name"]].append(x["cgpa"])
nosql = {k: round(sum(v)/len(v), 3) for k, v in g.items()}
for k in sorted(nosql): say(f"{k:30s}{nosql[k]}")

say("\n--- Cross-check against SQL (same question) ---")
sql = {r[0]: r[1] for r in con.execute("""
  WITH c AS (SELECT st.student_id, st.programme_id,
        1.0*SUM(g.grade_point*g.credit_units)/SUM(g.credit_units) AS cgpa
        FROM student st JOIN v_graded_result g USING(student_id) GROUP BY st.student_id)
  SELECT p.programme_name, ROUND(AVG(ROUND(c.cgpa,2)),3) FROM c JOIN programme p USING(programme_id) GROUP BY p.programme_id""")}
ok = all(abs(sql[k]-nosql[k]) < 0.002 for k in nosql)
say("NoSQL and SQL averages agree:", ok)

say("\n--- Q3 count students with at least one 'F' ($match results.grade == 'F') ---")
n = sum(1 for x in docs if any(r["grade"]=="F" for r in x["results"])); say(n, "students")
sqln = con.execute("SELECT COUNT(DISTINCT student_id) FROM v_graded_result WHERE grade='F'").fetchone()[0]
say("SQL cross-check:", sqln, "-> match:", n==sqln)

say("\n--- Key-value example (Redis-style result cache) ---")
cache = {f"cgpa:{x['_id']}": x["cgpa"] for x in docs[:3]}
for k,v in cache.items(): say(f"GET {k} -> {v}")
log.close()
