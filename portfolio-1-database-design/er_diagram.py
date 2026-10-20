"""Draws the ER diagram (simplified crow's-foot notation) to er_diagram.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# name: (x, top_y, attributes)
E = {
 "department":      (1.0, 15.0, ["PK dept_id","dept_name","faculty"]),
 "programme":       (5.5, 15.0, ["PK programme_id","programme_name","award","FK dept_id"]),
 "student":         (10.5, 15.0, ["PK student_id","matric_no","first_name","last_name","email","FK programme_id","entry_year","status"]),
 "lecturer":        (1.0, 10.0, ["PK lecturer_id","staff_no","full_name","email","FK dept_id"]),
 "course_offering": (5.5, 10.0, ["PK offering_id","FK course_id","FK semester_id","FK lecturer_id","capacity","seats_taken"]),
 "registration":    (10.5, 9.0, ["PK reg_id","FK student_id","FK offering_id","reg_date"]),
 "course":          (1.0, 5.0, ["PK course_id","course_code","title","credit_units","level","FK dept_id"]),
 "semester":        (5.5, 5.0, ["PK semester_id","session","term"]),
 "result":          (10.5, 4.6, ["PK/FK reg_id","ca_score","exam_score","total_score"]),
 "grade_scale":     (15.0, 4.6, ["PK grade","min_score","max_score","grade_point"]),
 "grade_audit":     (15.0, 10.0, ["PK audit_id","reg_id","old_total","new_total","changed_at"]),
}
W, ROW = 3.4, 0.5
fig, ax = plt.subplots(figsize=(15, 13)); ax.set_xlim(0, 19); ax.set_ylim(0, 16.5); ax.axis("off")
box = {}
for n,(x,top,f) in E.items():
    h = ROW*(len(f)+1)+0.25
    ax.add_patch(FancyBboxPatch((x,top-h),W,h,boxstyle="round,pad=0.02",fc="#eef3fb",ec="#0b3558",lw=1.6))
    ax.text(x+W/2,top-0.4,n,ha="center",va="center",fontweight="bold",color="#0b3558",fontsize=11)
    ax.plot([x,x+W],[top-0.72,top-0.72],color="#0b3558",lw=0.8)
    for i,a in enumerate(f):
        ax.text(x+0.2,top-1.05-ROW*i,a,fontsize=9.5,family="monospace",va="center",
                fontweight="bold" if a.startswith("PK") else "normal")
    box[n]=(x,top-h,W,h)
def pt(n,side,frac=0.5):
    x,y,w,h=box[n]
    return {"l":(x,y+h*frac),"r":(x+w,y+h*frac),"t":(x+w*frac,y+h),"b":(x+w*frac,y)}[side]
def line(p,q,one,many,r1=0.12,r2=0.88):
    ax.plot([p[0],q[0]],[p[1],q[1]],color="#c0392b",lw=1.5)
    for r,t in ((r1,one),(r2,many)):
        ax.text(p[0]+(q[0]-p[0])*r,p[1]+(q[1]-p[1])*r+0.22,t,color="#c0392b",fontweight="bold",ha="center",fontsize=11)
line(pt("department","r",0.6),pt("programme","l",0.6),"1","N")
line(pt("programme","r",0.6),pt("student","l",0.6),"1","N")
line(pt("department","b",0.5),pt("lecturer","t",0.5),"1","N")
line(pt("lecturer","r",0.5),pt("course_offering","l",0.5),"1","N")
line(pt("course","r",0.8),pt("course_offering","l",0.2),"1","N")
line(pt("semester","t",0.5),pt("course_offering","b",0.5),"1","N")
line(pt("course_offering","r",0.5),pt("registration","l",0.5),"1","N")
line(pt("student","b",0.5),pt("registration","t",0.5),"1","N")
line(pt("registration","b",0.5),pt("result","t",0.5),"1","1")
line(pt("grade_scale","l",0.5),pt("result","r",0.5),"1","N")
# department -> course along the left margin
x0=0.4; d=pt("department","l",0.5); c=pt("course","l",0.5)
ax.plot([d[0],x0,x0,c[0]],[d[1],d[1],c[1],c[1]],color="#c0392b",lw=1.5)
ax.text(x0+0.15,d[1]+0.2,"1",color="#c0392b",fontweight="bold",fontsize=11)
ax.text(x0+0.15,c[1]+0.2,"N",color="#c0392b",fontweight="bold",fontsize=11)
ax.text(9.5,16.1,"ER Diagram: University Student Result Portal (MIT 8103)",ha="center",fontsize=16,fontweight="bold")
ax.text(9.5,0.4,"Red labels: 1 = one side, N = many side. grade_audit is filled by a trigger on result updates (no FK, by design, so the log survives deletions).\n"
        "grade_scale relates to result by score range (total_score BETWEEN min_score AND max_score), not by a stored foreign key.",
        ha="center",fontsize=9.5)
plt.savefig("er_diagram.png",dpi=120,bbox_inches="tight")
