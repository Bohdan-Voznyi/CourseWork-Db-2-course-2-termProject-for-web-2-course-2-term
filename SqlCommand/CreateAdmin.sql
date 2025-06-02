IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'AdminInsurance')
    CREATE LOGIN AdminInsurance WITH PASSWORD = '1234';

USE insuranceSystem;

IF EXISTS (SELECT name FROM sys.database_principals WHERE name = 'AdminInsurance')
    DROP USER AdminInsurance;

CREATE USER AdminInsurance FOR LOGIN AdminInsurance;

ALTER ROLE db_datareader ADD MEMBER AdminInsurance;
ALTER ROLE db_datawriter ADD MEMBER AdminInsurance;
Grant execute to AdminInsurance;