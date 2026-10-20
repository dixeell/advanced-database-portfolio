# Normalisation explanation

**Unnormalised starting point.** A single "result sheet" row would look like:
`matric_no, student_name, email, programme, department, faculty, course_code, course_title, units, lecturer, lecturer_email, session, term, ca, exam, total, grade, grade_point`.

**1NF.** Every column holds one atomic value (no lists of courses in one cell) and each row is identified by a key (student + offering).

**2NF.** In the flat sheet the key is (student, course offering). Student name/email depend only on the student; course title/units only on the course; lecturer only on the offering. These partial dependencies were split into `student`, `course`, `course_offering` and `lecturer`. Only scores depend on the whole key, so they sit in `result` (keyed by `reg_id`, which stands for student + offering).

**3NF.** Transitive dependencies were removed: `programme -> department -> faculty` became `programme` and `department`; `total_score -> grade -> grade_point` became the `grade_scale` lookup table and the `v_graded_result` view, so grades are never stored redundantly and cannot disagree with the score. `total_score` is a generated column of `ca_score + exam_score`.

**BCNF.** Every determinant is a candidate key in each table (for example `matric_no` and `email` are unique keys of `student`; `(course_id, semester_id)` is a candidate key of `course_offering`).

**Deliberate denormalisation.** `course_offering.seats_taken` duplicates a COUNT of registrations. It is kept for fast capacity checks and protected by a CHECK constraint; Portfolio 3 shows how transactions keep it consistent.

## Keys and constraints (summary)
- Primary keys on every table; foreign keys with `PRAGMA foreign_keys = ON`.
- UNIQUE: `matric_no`, `email`, `course_code`, `staff_no`, `(student_id, offering_id)`, `(course_id, semester_id)`, `(session, term)`.
- CHECK: scores 0-40 / 0-60, credit units 1-6, capacity > 0, `seats_taken <= capacity`, status and award enumerations.
- Trigger `trg_result_audit` logs every score change into `grade_audit`.
