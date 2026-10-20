"""Creates university.db from schema.sql and loads reproducible synthetic data."""
import random, sqlite3, pathlib
HERE = pathlib.Path(__file__).parent
DB = HERE.parent / "university.db"
random.seed(8103)

FIRST = ["Aisha","Musa","Chinedu","Ngozi","Ibrahim","Fatima","Emeka","Zainab","Tunde","Amina",
         "Bola","Hauwa","Yusuf","Grace","Sadiq","Kemi","Uche","Halima","Segun","Blessing"]
LAST = ["Abdullahi","Okafor","Bello","Adeyemi","Usman","Nwosu","Lawal","Eze","Garba","Balogun",
        "Danjuma","Ojo","Sani","Chukwu","Aliyu","Obi","Mohammed","Olawale","Ahmed","Okonkwo"]
DEPTS = [("Computer Science","Science"),("Mathematics","Science"),("Accounting","Management Sciences"),
         ("Economics","Social Sciences"),("Electrical Engineering","Engineering")]
PROGS = [("BSc Computer Science","BSc",1),("BSc Software Engineering","BSc",1),("BSc Mathematics","BSc",2),
         ("BSc Accounting","BSc",3),("BSc Economics","BSc",4),("BSc Electrical Engineering","BSc",5),
         ("MSc Information Technology","MSc",1),("PGD Data Analytics","PGD",2)]
GRADES = [("A",70,100,5),("B",60,69,4),("C",50,59,3),("D",45,49,2),("E",40,44,1),("F",0,39,0)]

def main():
    if DB.exists(): DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript((HERE/"schema.sql").read_text())
    cur = con.cursor()
    cur.executemany("INSERT INTO department(dept_name,faculty) VALUES (?,?)", DEPTS)
    cur.executemany("INSERT INTO programme(programme_name,award,dept_id) VALUES (?,?,?)", PROGS)
    cur.executemany("INSERT INTO grade_scale VALUES (?,?,?,?)", GRADES)
    for i in range(1, 41):
        n = random.choice(FIRST)+" "+random.choice(LAST)
        cur.execute("INSERT INTO lecturer(staff_no,full_name,email,dept_id) VALUES (?,?,?,?)",
                    (f"STF{i:04d}", n, f"staff{i}@uni.edu.ng", random.randint(1,5)))
    code_prefix = {1:"CSC",2:"MTH",3:"ACC",4:"ECO",5:"EEE"}
    cid = 0
    for d in range(1,6):
        for k in range(24):
            cid += 1
            lvl = random.choice([100,200,300,400])
            cur.execute("INSERT INTO course(course_code,title,credit_units,level,dept_id) VALUES (?,?,?,?,?)",
                        (f"{code_prefix[d]}{lvl//100}{k:02d}", f"{code_prefix[d]} Topic {k}", random.choice([2,3,3,4]), lvl, d))
    sems = [("2024/2025","First"),("2024/2025","Second"),("2025/2026","First"),("2025/2026","Second")]
    cur.executemany("INSERT INTO semester(session,term) VALUES (?,?)", sems)
    for s in range(1,5):
        for c in range(1,121):
            if random.random() < 0.6:
                cur.execute("INSERT INTO course_offering(course_id,semester_id,lecturer_id,capacity) VALUES (?,?,?,?)",
                            (c, s, random.randint(1,40), random.choice([80,100,150,200])))
    n_students = 2000
    for i in range(1, n_students+1):
        fn, ln = random.choice(FIRST), random.choice(LAST)
        yr = random.randint(2022, 2025)
        cur.execute("INSERT INTO student(matric_no,first_name,last_name,email,programme_id,entry_year,status) VALUES (?,?,?,?,?,?,?)",
                    (f"MIT/{yr}/{i:05d}", fn, ln, f"{fn.lower()}.{ln.lower()}{i}@students.uni.edu.ng",
                     random.randint(1,8), yr, random.choices(["active","withdrawn","graduated"],[90,4,6])[0]))
    offerings = [r[0] for r in cur.execute("SELECT offering_id FROM course_offering")]
    for sid in range(1, n_students+1):
        for off in random.sample(offerings, 20):
            cur.execute("INSERT INTO registration(student_id,offering_id,reg_date) VALUES (?,?,?)",
                        (sid, off, f"2025-{random.randint(1,9):02d}-{random.randint(1,28):02d}"))
    regs = [r[0] for r in cur.execute("SELECT reg_id FROM registration")]
    for rid in regs:
        ca = min(40, max(0, int(random.gauss(26, 7))))
        ex = min(60, max(0, int(random.gauss(33, 13))))
        cur.execute("INSERT INTO result(reg_id,ca_score,exam_score) VALUES (?,?,?)", (rid, ca, ex))
    # keep seats_taken consistent with registrations
    cur.execute("""UPDATE course_offering SET seats_taken =
                   MIN(capacity, (SELECT COUNT(*) FROM registration r WHERE r.offering_id = course_offering.offering_id))""")
    con.commit()
    for t in ["department","programme","student","lecturer","course","semester","course_offering","registration","result"]:
        print(f"{t:18s}{cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>8d}")
    con.close()

if __name__ == "__main__":
    main()
