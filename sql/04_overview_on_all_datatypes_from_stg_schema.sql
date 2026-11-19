-- Overview on all tables from stg Schema
SELECT 
    table_name, 
    column_name, 
    data_type
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_schema = 'stg'
ORDER BY table_name, ordinal_position;