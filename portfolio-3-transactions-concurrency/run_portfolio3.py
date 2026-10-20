"""Portfolio 3: transactions (commit/rollback), isolation, and a concurrency
anomaly (overbooking from a lost update) with two fixes. Works on a COPY of the DB."""
import sqlite3, shutil, threading, pathlib, sys
HERE = pathlib.Path(__file__).parent
OUT = HERE/"output"; OUT.mkdir(exist_ok=True)
DB = OUT/"p3_test.db"
shutil.copy(HERE.parent/"university.db", DB)
log = open(OUT/"transaction_log.txt","w")
def say(*a):
    s=" ".join(str(x) for x in a); print(s); log.write(s+"\n")
def conn(**kw):
    c = sqlite3.connect(DB, timeout=10, isolation_level=None, **kw)   # manual BEGIN/COMMIT
    c.execute("PRAGMA foreign_keys=ON"); return c

def seats(c, off): return c.execute("SELECT seats_taken,capacity FROM course_offering WHERE offering_id=?",(off,)).fetchone()
def nregs(c, off): return c.execute("SELECT COUNT(*) FROM registration WHERE offering_id=?",(off,)).fetchone()[0]

# A fresh offering with capacity 2 for the demos
c = conn()
c.execute("INSERT INTO course_offering(offering_id,course_id,semester_id,lecturer_id,capacity,seats_taken) VALUES (9001,1,4,1,2,0)")
c.execute("INSERT INTO course_offering(offering_id,course_id,semester_id,lecturer_id,capacity,seats_taken) VALUES (9002,2,4,1,1,0)")
# students 1990..1999 have no registrations in offerings 9001/9002

def register(c, student, off):
    """Atomic course registration: insert registration + increment seats_taken."""
    c.execute("BEGIN IMMEDIATE")
    try:
        c.execute("INSERT INTO registration(student_id,offering_id) VALUES (?,?)",(student,off))
        c.execute("UPDATE course_offering SET seats_taken = seats_taken + 1 WHERE offering_id=?",(off,))
        c.execute("COMMIT"); return "COMMITTED"
    except sqlite3.Error as e:
        c.execute("ROLLBACK"); return f"ROLLED BACK ({type(e).__name__}: {e})"

say("=== 1. COMMIT: valid registration ===")
say("before:", seats(c,9001), "registrations:", nregs(c,9001))
say("student 1990 ->", register(c,1990,9001))
say("after :", seats(c,9001), "registrations:", nregs(c,9001))

say("\n=== 2a. ROLLBACK: duplicate registration (UNIQUE violation) ===")
say("student 1990 again ->", register(c,1990,9001))
say("state unchanged:", seats(c,9001), "registrations:", nregs(c,9001))

say("\n=== 2b. ROLLBACK: course full (CHECK seats_taken <= capacity fails AFTER the INSERT) ===")
say("student 1991 ->", register(c,1991,9001), "(fills the course)")
say("student 1992 ->", register(c,1992,9001))
say("state:", seats(c,9001), "registrations:", nregs(c,9001), "<- the half-done INSERT was undone, no orphan row")

say("\n=== 2c. Grade correction with audit trigger: COMMIT then ROLLBACK ===")
reg = c.execute("SELECT reg_id,ca_score,exam_score FROM result LIMIT 1").fetchone()
say("result before:", reg)
c.execute("BEGIN"); c.execute("UPDATE result SET exam_score=exam_score+1 WHERE reg_id=?",(reg[0],)); c.execute("COMMIT")
say("audit rows for reg", reg[0], ":", c.execute("SELECT old_total,new_total FROM grade_audit WHERE reg_id=?",(reg[0],)).fetchall())
c.execute("BEGIN")
try:
    c.execute("UPDATE result SET exam_score=99 WHERE reg_id=?",(reg[0],))   # violates CHECK <= 60
    c.execute("COMMIT")
except sqlite3.Error as e:
    c.execute("ROLLBACK"); say("invalid score rejected and rolled back:", e)
say("result after :", c.execute("SELECT reg_id,ca_score,exam_score FROM result WHERE reg_id=?",(reg[0],)).fetchone())

say("\n=== 3. ISOLATION: no dirty reads (WAL mode snapshot) ===")
c.execute("PRAGMA journal_mode=WAL")
w, r = conn(), conn()
w.execute("BEGIN"); w.execute("UPDATE course_offering SET capacity=500 WHERE offering_id=9001")
say("writer (uncommitted) sees capacity:", w.execute("SELECT capacity FROM course_offering WHERE offering_id=9001").fetchone()[0])
say("reader sees capacity            :", r.execute("SELECT capacity FROM course_offering WHERE offering_id=9001").fetchone()[0], "<- uncommitted change invisible")
w.execute("ROLLBACK")
say("after ROLLBACK reader sees      :", r.execute("SELECT capacity FROM course_offering WHERE offering_id=9001").fetchone()[0])
w.close(); r.close()

# ---------- 4. Concurrency anomaly ----------
def run_threads(worker, students, off):
    barrier = threading.Barrier(len(students)); res = {}
    def go(s):
        cc = conn(); res[s] = worker(cc, s, off, barrier); cc.close()
    ts=[threading.Thread(target=go,args=(s,)) for s in students]
    [t.start() for t in ts]; [t.join() for t in ts]; return res

def naive(cc, s, off, barrier):
    """Read-check-write with NO transaction: classic lost update."""
    taken, cap = seats(cc, off)
    barrier.wait()                      # both threads now hold the same stale 'taken'
    if taken < cap:
        cc.execute("INSERT INTO registration(student_id,offering_id) VALUES (?,?)",(s,off))
        cc.execute("UPDATE course_offering SET seats_taken=? WHERE offering_id=?",(taken+1,off))
        return "registered"
    return "rejected: full"

def locked(cc, s, off, barrier):
    """Fix 1: BEGIN IMMEDIATE takes the write lock BEFORE the read, serialising the check."""
    barrier.wait()
    cc.execute("BEGIN IMMEDIATE")
    taken, cap = seats(cc, off)
    if taken < cap:
        cc.execute("INSERT INTO registration(student_id,offering_id) VALUES (?,?)",(s,off))
        cc.execute("UPDATE course_offering SET seats_taken=seats_taken+1 WHERE offering_id=?",(off,))
        cc.execute("COMMIT"); return "registered"
    cc.execute("ROLLBACK"); return "rejected: full"

def atomic(cc, s, off, barrier):
    """Fix 2: one conditional UPDATE does check+increment atomically."""
    barrier.wait()
    cc.execute("BEGIN IMMEDIATE")
    n = cc.execute("UPDATE course_offering SET seats_taken=seats_taken+1 WHERE offering_id=? AND seats_taken<capacity",(off,)).rowcount
    if n == 1:
        cc.execute("INSERT INTO registration(student_id,offering_id) VALUES (?,?)",(s,off)); cc.execute("COMMIT"); return "registered"
    cc.execute("ROLLBACK"); return "rejected: full"

def reset(off):
    cc = conn(); cc.execute("DELETE FROM registration WHERE offering_id=?",(off,))
    cc.execute("UPDATE course_offering SET seats_taken=0 WHERE offering_id=?",(off,)); cc.close()

def report(title, worker):
    reset(9002)                                # capacity = 1
    res = run_threads(worker,[1993,1994,1995],9002)
    cc = conn(); t,cap = seats(cc,9002); n = nregs(cc,9002); cc.close()
    verdict = "CONSISTENT" if n <= cap and t == n else "ANOMALY: overbooked / counter wrong"
    say(f"\n--- {title} ---\nthread outcomes: {res}\nfinal seats_taken={t}, capacity={cap}, registration rows={n} -> {verdict}")

say("\n=== 4. CONCURRENCY: 3 students race for the LAST seat (capacity 1) ===")
report("4a. Uncontrolled read-modify-write", naive)
report("4b. Fix 1: BEGIN IMMEDIATE (pessimistic lock)", locked)
report("4c. Fix 2: atomic conditional UPDATE", atomic)
log.close()
