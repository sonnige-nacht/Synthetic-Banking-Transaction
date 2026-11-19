-- Data Cleaning


-- 1.1 Convert timestamp to several columns

ALTER TABLE stg.transactions
ADD
    transaction_time datetimeoffset,
    transaction_hour int,
    transaction_minute int,
    day_of_week nvarchar(20),
    day_of_month int,
    transaction_month int,
    transaction_year int,
    is_night int;

-- 1.2 Fill the created Columns
UPDATE stg.transactions
SET
    transaction_time = TRY_CONVERT(datetimeoffset, [timestamp]),
    transaction_hour = DATEPART(HOUR, TRY_CONVERT(datetimeoffset, [timestamp])),
    transaction_minute = DATEPART(MINUTE, TRY_CONVERT(datetimeoffset, [timestamp])),
    day_of_week = DATENAME(WEEKDAY, TRY_CONVERT(datetimeoffset, [timestamp])),
    day_of_month = DATEPART(DAY, TRY_CONVERT(datetimeoffset, [timestamp])),
    transaction_month = DATEPART(MONTH, TRY_CONVERT(datetimeoffset, [timestamp])),
    transaction_year = DATEPART(YEAR, TRY_CONVERT(datetimeoffset, [timestamp])),
    is_night =
        CASE
            WHEN DATEPART(HOUR, TRY_CONVERT(datetimeoffset, [timestamp])) BETWEEN 0 AND 5
            THEN 1
            ELSE 0
        END;


-- 2.1 Convert is_fraud column to int from bigint

ALTER TABLE stg.fraud_status
ALTER COLUMN is_fraud INT;