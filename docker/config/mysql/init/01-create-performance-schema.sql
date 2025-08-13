-- MySQL 8.4 Performance Monitoring Setup for Laravel Performance Testing

-- Enable performance schema if not already enabled
SET GLOBAL performance_schema = ON;

-- Create database for performance monitoring
CREATE DATABASE IF NOT EXISTS percona;
USE percona;

-- Create query review table for pt-query-digest
CREATE TABLE IF NOT EXISTS query_review (
                                            checksum     BIGINT UNSIGNED NOT NULL PRIMARY KEY,
                                            fingerprint  TEXT NOT NULL,
                                            sample       TEXT NOT NULL,
                                            first_seen   DATETIME,
                                            last_seen    DATETIME,
                                            reviewed_by  VARCHAR(20),
                                            reviewed_on  DATETIME,
                                            comments     TEXT,
                                            reviewed_status ENUM('','new','reviewed','ignore') DEFAULT 'new'
);

-- Create query review history table
CREATE TABLE IF NOT EXISTS query_review_history (
                                                    checksum               BIGINT UNSIGNED NOT NULL,
                                                    sample                 TEXT NOT NULL,
                                                    ts_min                 DATETIME NOT NULL,
                                                    ts_max                 DATETIME NOT NULL,
                                                    ts_cnt                 FLOAT,
                                                    Query_time_sum         FLOAT,
                                                    Query_time_min         FLOAT,
                                                    Query_time_max         FLOAT,
                                                    Query_time_pct_95      FLOAT,
                                                    Query_time_stddev      FLOAT,
                                                    Query_time_median      FLOAT,
                                                    Lock_time_sum          FLOAT,
                                                    Lock_time_min          FLOAT,
                                                    Lock_time_max          FLOAT,
                                                    Lock_time_pct_95       FLOAT,
                                                    Lock_time_stddev       FLOAT,
                                                    Lock_time_median       FLOAT,
                                                    Rows_sent_sum          FLOAT,
                                                    Rows_sent_min          FLOAT,
                                                    Rows_sent_max          FLOAT,
                                                    Rows_sent_pct_95       FLOAT,
                                                    Rows_sent_stddev       FLOAT,
                                                    Rows_sent_median       FLOAT,
                                                    Rows_examined_sum      FLOAT,
                                                    Rows_examined_min      FLOAT,
                                                    Rows_examined_max      FLOAT,
                                                    Rows_examined_pct_95   FLOAT,
                                                    Rows_examined_stddev   FLOAT,
                                                    Rows_examined_median   FLOAT,
                                                    hostname_max           VARCHAR(64) NOT NULL,
                                                    PRIMARY KEY (checksum, ts_min, ts_max)
);

-- Create user for monitoring tools
CREATE USER IF NOT EXISTS 'monitor'@'%' IDENTIFIED BY 'monitor';
GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO 'monitor'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER ON percona.* TO 'monitor'@'%';

-- Create user for ProxySQL
CREATE USER IF NOT EXISTS 'proxysql'@'%' IDENTIFIED BY 'proxysql';
GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO 'proxysql'@'%';

-- Enable additional performance monitoring
UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES'
WHERE NAME LIKE '%statement/%';

UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES'
WHERE NAME LIKE '%stage/%';

UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES'
WHERE NAME LIKE '%wait/io/%';

-- Enable events statements history
UPDATE performance_schema.setup_consumers SET ENABLED = 'YES'
WHERE NAME LIKE '%events_statements_%';

-- Enable events waits history
UPDATE performance_schema.setup_consumers SET ENABLED = 'YES'
WHERE NAME LIKE '%events_waits_%';

-- Create Laravel performance monitoring tables
USE laravel_perf;

-- Create performance metrics table for custom tracking
CREATE TABLE IF NOT EXISTS performance_metrics (
                                                   id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                                   endpoint VARCHAR(255) NOT NULL,
                                                   method VARCHAR(10) NOT NULL,
                                                   response_time_ms DECIMAL(10,2) NOT NULL,
                                                   memory_usage_mb DECIMAL(10,2) NOT NULL,
                                                   query_count INT NOT NULL,
                                                   cache_hits INT DEFAULT 0,
                                                   cache_misses INT DEFAULT 0,
                                                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                   INDEX idx_endpoint_method (endpoint, method),
                                                   INDEX idx_response_time (response_time_ms),
                                                   INDEX idx_created_at (created_at)
);

-- Create slow queries tracking table
CREATE TABLE IF NOT EXISTS slow_queries (
                                            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                            query_hash VARCHAR(64) NOT NULL,
                                            query_text TEXT NOT NULL,
                                            execution_time_ms DECIMAL(10,2) NOT NULL,
                                            rows_examined INT NOT NULL,
                                            rows_sent INT NOT NULL,
                                            endpoint VARCHAR(255),
                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                            UNIQUE KEY unique_hash (query_hash),
                                            INDEX idx_execution_time (execution_time_ms),
                                            INDEX idx_endpoint (endpoint),
                                            INDEX idx_created_at (created_at)
);

-- Create memory usage tracking table
CREATE TABLE IF NOT EXISTS memory_usage (
                                            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                                            process_type ENUM('web', 'queue', 'cli') NOT NULL,
                                            peak_memory_mb DECIMAL(10,2) NOT NULL,
                                            average_memory_mb DECIMAL(10,2) NOT NULL,
                                            endpoint VARCHAR(255),
                                            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                            INDEX idx_process_type (process_type),
                                            INDEX idx_peak_memory (peak_memory_mb),
                                            INDEX idx_recorded_at (recorded_at)
);

-- Create indexes for Laravel application tables (will be created by migrations)
-- These are examples of the performance indexes that would be added

-- Example: Add indexes for common Laravel query patterns
-- ALTER TABLE users ADD INDEX idx_email_verified (email, email_verified_at);
-- ALTER TABLE users ADD INDEX idx_created_at (created_at);

-- Example: Add composite indexes for order queries
-- ALTER TABLE orders ADD INDEX idx_user_status_created (user_id, status, created_at);
-- ALTER TABLE orders ADD INDEX idx_status_created (status, created_at);

-- Example: Add indexes for product catalog
-- ALTER TABLE products ADD INDEX idx_category_active (category_id, is_active);
-- ALTER TABLE products ADD INDEX idx_price_range (price, is_active);

-- Create views for common performance queries
CREATE VIEW IF NOT EXISTS slow_query_summary AS
SELECT
    endpoint,
    COUNT(*) as slow_query_count,
    AVG(execution_time_ms) as avg_execution_time,
    MAX(execution_time_ms) as max_execution_time,
    AVG(rows_examined) as avg_rows_examined
FROM slow_queries
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY endpoint
ORDER BY avg_execution_time DESC;

CREATE VIEW IF NOT EXISTS performance_summary AS
SELECT
    endpoint,
    method,
    COUNT(*) as request_count,
    AVG(response_time_ms) as avg_response_time,
    MAX(response_time_ms) as max_response_time,
    AVG(memory_usage_mb) as avg_memory_usage,
    AVG(query_count) as avg_query_count,
    SUM(cache_hits) / (SUM(cache_hits) + SUM(cache_misses)) * 100 as cache_hit_ratio
FROM performance_metrics
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
GROUP BY endpoint, method
ORDER BY avg_response_time DESC;

-- Grant permissions for Laravel application
GRANT SELECT, INSERT, UPDATE ON laravel_perf.performance_metrics TO 'laravel'@'%';
GRANT SELECT, INSERT, UPDATE ON laravel_perf.slow_queries TO 'laravel'@'%';
GRANT SELECT, INSERT, UPDATE ON laravel_perf.memory_usage TO 'laravel'@'%';
GRANT SELECT ON laravel_perf.slow_query_summary TO 'laravel'@'%';
GRANT SELECT ON laravel_perf.performance_summary TO 'laravel'@'%';

-- Flush privileges
FLUSH PRIVILEGES;