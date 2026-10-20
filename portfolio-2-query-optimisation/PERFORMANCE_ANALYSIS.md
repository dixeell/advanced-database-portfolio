# Portfolio 2: Performance analysis

Setup: SQLite 3.53, 40,000 registrations, 2,000 students, median of 30 runs on the build machine. Absolute times vary by machine; the *plans* and relative changes are what matter. Full plans are in `output/execution\_plans\_before\_after.txt`; query results in `output/queries\_and\_results.txt`; rerun with `python3 run\_portfolio2.py`.

|Experiment|Index added|Plan before|Plan after|Before|After|
|-|-|-|-|-|-|
|O1 class list for one offering|`registration(offering\_id)`|scans `student`, probes `registration` per student|`SEARCH reg USING INDEX (offering\_id=?)`|0.994 ms|0.279 ms (3.6x)|
|O2 active students per programme/intake|`student(programme\_id, status, entry\_year)`|`SCAN student`|covering index search|0.228 ms|0.088 ms (2.6x)|
|O3 failing results (< 40)|`result(total\_score)`|`SCAN result`|index range search|3.130 ms|0.321 ms (9.7x)|
|O4 registrations in a semester|`course\_offering(semester\_id)`|covering index scan of 269 rows|covering index search|0.482 ms|0.484 ms (no gain)|

**Findings.**

1. The existing `UNIQUE(student\_id, offering\_id)` index only helps when `student\_id` is the leading column, so lookups by `offering\_id` alone needed their own index (O1). Column order in composite indexes matters.
2. A composite index whose columns match the equality filters (O2) turned a full scan into a covering search, so the table was never touched.
3. A generated column can be indexed (O3), so a score-range report no longer scans every result.
4. **Negative result (O4):** the offerings table has only 269 rows, so the index gave no benefit. Indexes cost write time and space, so they should be justified by plans and measurements, not added by habit.
5. **Query rewrite:** replacing a correlated subquery with `LEFT JOIN ... GROUP BY` returned identical results but was *not* faster here (1.62 ms vs 0.58 ms). SQLite handles the correlated count well because the inner lookup uses an index, so the rewrite was not worth keeping.

**Trade-off.** Each added index slows INSERT/UPDATE slightly; this workload is read-heavy (transcripts, reports) with bursts of writes during result entry, so the read gains justify O1-O3.

