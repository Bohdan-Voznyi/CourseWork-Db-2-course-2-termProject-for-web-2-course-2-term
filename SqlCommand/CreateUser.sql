

if not exists (select name from sys.server_principals where name  = 'UserInsurance')
	create login UserInsurance with password = '1234';


use insuranceSystem;


if exists (select name from sys.database_principals where name = 'UserInsurance')
   drop user UserInsurance;


create user UserInsurance from login UserInsurance


alter role db_datareader add member UserInsurance

