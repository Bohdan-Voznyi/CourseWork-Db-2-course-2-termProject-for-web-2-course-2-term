USE insuranceSystem;
GO

-- Видалення таблиць у правильному порядку, щоб уникнути проблем із зовнішніми ключами
IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Payment')
DROP TABLE Payment;
GO

IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Claim')
DROP TABLE Claim;
GO

IF EXISTS (SELECT name FROM sys.objects WHERE name = 'InsurancePolicy')
DROP TABLE InsurancePolicy;
GO

IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Vehicle')
DROP TABLE Vehicle;
GO

IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Client')
DROP TABLE Client;
GO

IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Employee')
DROP TABLE Employee;
GO

-- Створення таблиці Employee (Працівник страхової компанії)
CREATE TABLE Employee (
	id Char(36) PRIMARY KEY,
	full_name NVARCHAR(MAX) NOT NULL,
	position NVARCHAR(MAX) NOT NULL,
	phone NVARCHAR(50) NOT NULL,
	email NVARCHAR(255) NOT NULL
);
GO

-- Створення таблиці Client (Клієнт)
CREATE TABLE Client (
	id Char(36) PRIMARY KEY,
	full_name NVARCHAR(MAX) NOT NULL,
	address NVARCHAR(MAX) NOT NULL,
	phone NVARCHAR(50) NOT NULL,
	email NVARCHAR(255) NOT NULL,
	passport_number NVARCHAR(50) NOT NULL
);
GO

-- Створення таблиці Vehicle (Автомобіль)
CREATE TABLE Vehicle (
	id Char(36) PRIMARY KEY,
	owner_id Char(36) NOT NULL, -- Виправлення типу на Char(36)
	make NVARCHAR(100) NOT NULL,
	model NVARCHAR(100) NOT NULL,
	year INT NOT NULL,
	license_plate NVARCHAR(50) NOT NULL,
	vin NVARCHAR(100) NOT NULL,

	FOREIGN KEY (owner_id) REFERENCES Client(id)
);
GO

-- Створення таблиці InsurancePolicy (Страховий поліс)
CREATE TABLE InsurancePolicy (
	id Char(36) PRIMARY KEY,
	policy_number NVARCHAR(100) NOT NULL,
	client_id Char(36) NOT NULL, -- Виправлення типу на Char(36)
	vehicle_id Char(36) NOT NULL, -- Виправлення типу на Char(36)
	employee_id Char(36) NOT NULL, -- Виправлення типу на Char(36)
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	insurance_type NVARCHAR(100) NOT NULL,
	premium_amount DECIMAL(18,2) NOT NULL,
	status NVARCHAR(50) NOT NULL,

	FOREIGN KEY (client_id) REFERENCES Client(id),
	FOREIGN KEY (vehicle_id) REFERENCES Vehicle(id),
	FOREIGN KEY (employee_id) REFERENCES Employee(id)
);
GO

-- Створення таблиці Claim (Подія / страховий випадок)
CREATE TABLE Claim (
	id Char(36) PRIMARY KEY,
	policy_id Char(36) NOT NULL, -- Виправлення типу на Char(36)
	claim_date DATE NOT NULL,
	description NVARCHAR(MAX) NOT NULL,
	damage_amount DECIMAL(18,2) NOT NULL,
	is_approved BIT NOT NULL,

	FOREIGN KEY (policy_id) REFERENCES InsurancePolicy(id)
);
GO

-- Створення таблиці Payment (Виплата по страховому випадку)
CREATE TABLE Payment (
	id Char(36) PRIMARY KEY,
	claim_id Char(36) NOT NULL, -- Виправлення типу на Char(36)
	payment_date DATE NOT NULL,
	amount DECIMAL(18,2) NOT NULL,
	method NVARCHAR(100) NOT NULL,

	FOREIGN KEY (claim_id) REFERENCES Claim(id)
);
GO




IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Users')
DROP TABLE Users;
GO
CREATE TABLE Users (
    Id char(36) PRIMARY KEY,
    Username NVARCHAR(100),
    Password NVARCHAR(100), -- In a real app, store hashed passwords
    Roleuser NVARCHAR(50) -- 'admin', 'user'
);


delete from Users
go

INSERT INTO Users(Id, Username, Password, Roleuser)
VALUES 
('11111111-1111-1111-1111-111111111111', 'sa', '1234', 'Admin'),
('22222222-2222-2222-2222-222222222222', 'Admin', 'admin123', 'Admin'),
('33333333-3333-3333-3333-333333333333', 'worker', 'worker123', 'worker');
go