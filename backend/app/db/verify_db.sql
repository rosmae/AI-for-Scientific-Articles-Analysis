-- Verify PostgreSQL database and transaction status

-- Check for active transactions
SELECT pid, 
       usename, 
       application_name,
       client_addr, 
       backend_start,
       state, 
       state_change,
       query
FROM pg_stat_activity 
WHERE datname = current_database()
AND state = 'idle in transaction';

-- Check for locks
SELECT locktype, 
       relation::regclass, 
       mode, 
       transactionid, 
       pid, 
       granted
FROM pg_locks l 
JOIN pg_stat_activity s ON l.pid = s.pid
WHERE s.datname = current_database();

-- Check database stats
SELECT * FROM pg_stat_database 
WHERE datname = current_database();

-- Commands to fix issues (run as needed):

-- 1. To terminate a specific connection (replace PID with actual process ID)
-- SELECT pg_terminate_backend(PID);

-- 2. To terminate all idle transactions
-- SELECT pg_terminate_backend(pid) 
-- FROM pg_stat_activity 
-- WHERE datname = current_database() 
-- AND state = 'idle in transaction';

-- 3. To cancel a specific query (replace PID with actual process ID)
-- SELECT pg_cancel_backend(PID);
