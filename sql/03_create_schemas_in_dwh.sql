-- 1. Create schemas
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'raw') 
    EXEC('CREATE SCHEMA raw');

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'stg') 
    EXEC('CREATE SCHEMA stg');

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'dw') 
    EXEC('CREATE SCHEMA dw');
GO