# Portfolio 3: Transactions and Concurrency

Run `python3 run_portfolio3.py` (works on a copy of the database). Output: `output/transaction_log.txt`.

| Demonstration | Result |
|---|---|
| Valid course registration | COMMIT: registration row and `seats_taken` both change |
| Duplicate registration | UNIQUE violation, ROLLBACK, nothing changes |
| Registration when course is full | CHECK fails *after* the INSERT; ROLLBACK removes the half-done row (atomicity) |
| Grade correction | COMMIT writes an audit row via trigger; invalid score (99) is rejected and rolled back |
| Isolation | A reader never sees the writer's uncommitted change (no dirty read) |
| **Concurrency anomaly** | 3 students race for the last seat with an uncontrolled read-modify-write: all 3 register, capacity 1 (**overbooked**, counter says 1) |
| Fix 1 | `BEGIN IMMEDIATE` (lock before reading): exactly 1 registers |
| Fix 2 | Atomic conditional `UPDATE ... WHERE seats_taken < capacity`: exactly 1 registers |

**SQLite note.** SQLite is always serialisable and has a single writer, so it cannot show READ COMMITTED vs REPEATABLE READ differences. `postgres_isolation_levels.sql` covers those; it is **UNTESTED here**, so run it in two psql sessions and add screenshots under `evidence/`.
