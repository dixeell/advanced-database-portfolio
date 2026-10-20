-- UNTESTED in the build sandbox (no PostgreSQL there). Run in TWO psql sessions and screenshot both.
-- Demonstrates non-repeatable read (READ COMMITTED) vs snapshot isolation (REPEATABLE READ).
CREATE TABLE IF NOT EXISTS offering_demo (offering_id int PRIMARY KEY, capacity int, seats_taken int);
INSERT INTO offering_demo VALUES (1, 100, 50) ON CONFLICT DO NOTHING;

-- ===== Session A =====                         -- ===== Session B =====
-- BEGIN ISOLATION LEVEL READ COMMITTED;
-- SELECT seats_taken FROM offering_demo WHERE offering_id=1;   -- 50
--                                                 BEGIN; UPDATE offering_demo SET seats_taken=51 WHERE offering_id=1; COMMIT;
-- SELECT seats_taken FROM offering_demo WHERE offering_id=1;   -- 51 (non-repeatable read)
-- COMMIT;

-- Reset: UPDATE offering_demo SET seats_taken=50 WHERE offering_id=1;
-- BEGIN ISOLATION LEVEL REPEATABLE READ;
-- SELECT seats_taken FROM offering_demo WHERE offering_id=1;   -- 50
--                                                 BEGIN; UPDATE offering_demo SET seats_taken=51 WHERE offering_id=1; COMMIT;
-- SELECT seats_taken FROM offering_demo WHERE offering_id=1;   -- still 50 (snapshot)
-- UPDATE offering_demo SET seats_taken=seats_taken+1 WHERE offering_id=1;
--   -- ERROR: could not serialize access due to concurrent update (retry the transaction)
-- ROLLBACK;

-- Pessimistic locking fix for the overbooking race:
-- BEGIN; SELECT seats_taken, capacity FROM offering_demo WHERE offering_id=1 FOR UPDATE;
-- (a second session running the same SELECT ... FOR UPDATE now waits until the first COMMITs)
