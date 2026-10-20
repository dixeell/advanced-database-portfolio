# Portfolio 4: NoSQL and Advanced Data Models

**Model chosen: document (MongoDB) for the transcript workload, plus a key-value cache example.**

- `export_to_documents.py` converts the relational data to one document per student with embedded `results` and a pre-computed `cgpa`.
- `run_portfolio4.py` runs the equivalent of the queries in `mongodb_queries.js` in Python and **cross-checks every answer against SQL** (averages per programme agree; 1,808 students with at least one F matches). Output: `output/nosql_results.txt`.
- `mongodb_queries.js` holds the real mongosh commands (indexes, `findOne`, `$group`, `$unwind`). **UNTESTED here** (no MongoDB server); run it after `mongoimport` and add screenshots.

**Why a document model suits this case.** The dominant read is "show me this student's transcript": one `_id` lookup returns everything, with no joins. Results are naturally owned by one student and bounded in size (a student has dozens, not millions). Schema flexibility helps when programmes carry different assessment components.

**Where it does not suit.** Cross-cutting questions (fail rate per course across all students, lecturer workload) need `$unwind` over every document and duplicate course data inside each student; capacity checks and grade corrections need multi-document consistency, so relational SQL stays the system of record. The recommended design is polyglot: SQL for writes and integrity, MongoDB for read-optimised transcripts, Redis for hot CGPA lookups (`GET cgpa:<matric>`).
