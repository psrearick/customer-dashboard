#!/bin/bash
# Script to analyze MySQL slow query logs

# Wait for MySQL to be ready
while ! mysqladmin ping -h mysql -u root -prootpassword --silent; do
    sleep 1
done

# Generate slow query analysis
pt-query-digest \
    --type=slowlog \
    --review h=mysql,D=percona,t=query_review \
    --history h=mysql,D=percona,t=query_review_history \
    --no-report \
    --limit=95%:20 \
    --filter='$event->{Rows_examined} <= 1000' \
    /var/lib/mysql/slow.log

echo "Slow query analysis completed. Check percona.query_review table for results."
