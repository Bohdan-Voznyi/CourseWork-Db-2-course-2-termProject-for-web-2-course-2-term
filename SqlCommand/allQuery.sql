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
    owner_id Char(36) NOT NULL,
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
    client_id Char(36) NOT NULL,
    vehicle_id Char(36) NOT NULL,
    employee_id Char(36) NOT NULL,
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
    policy_id Char(36) NOT NULL,
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
    claim_id Char(36) NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    method NVARCHAR(100) NOT NULL,
    FOREIGN KEY (claim_id) REFERENCES Claim(id)
);
GO

-- Створення таблиці Users (Користувачі системи)
IF EXISTS (SELECT name FROM sys.objects WHERE name = 'Users')
DROP TABLE Users;
GO

CREATE TABLE Users (
    Id char(36) PRIMARY KEY,
    Username NVARCHAR(100),
    Password NVARCHAR(100), -- In a real app, store hashed passwords
    Roleuser NVARCHAR(50) -- 'admin', 'user'
);
GO

-- Додавання тестових користувачів
INSERT INTO Users(Id, Username, Password, Roleuser)
VALUES 
('11111111-1111-1111-1111-111111111111', 'sa', '1234', 'Admin'),
('22222222-2222-2222-2222-222222222222', 'Admin', 'admin123', 'Admin'),
('33333333-3333-3333-3333-333333333333', 'worker', 'worker123', 'worker');
GO

-- =============================================
-- Stored Procedures for Client operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_AddClient
    @id Char(36),
    @full_name NVARCHAR(MAX),
    @address NVARCHAR(MAX),
    @phone NVARCHAR(50),
    @email NVARCHAR(255),
    @passport_number NVARCHAR(50)
AS
BEGIN
    INSERT INTO Client (id, full_name, address, phone, email, passport_number)
    VALUES (@id, @full_name, @address, @phone, @email, @passport_number);
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdateClient
    @id Char(36),
    @full_name NVARCHAR(MAX),
    @address NVARCHAR(MAX),
    @phone NVARCHAR(50),
    @email NVARCHAR(255),
    @passport_number NVARCHAR(50)
AS
BEGIN
    UPDATE Client 
    SET full_name = @full_name,
        address = @address,
        phone = @phone,
        email = @email,
        passport_number = @passport_number
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_DeleteClient
    @id Char(36)
AS
BEGIN
    DELETE FROM Client WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetAllClients
AS
BEGIN
    SELECT id, full_name, address, phone, email, passport_number 
    FROM Client;
END;
GO

-- =============================================
-- Stored Procedures for Employee operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_AddEmployee
    @id Char(36),
    @full_name NVARCHAR(MAX),
    @position NVARCHAR(MAX),
    @phone NVARCHAR(50),
    @email NVARCHAR(255)
AS
BEGIN
    INSERT INTO Employee (id, full_name, position, phone, email)
    VALUES (@id, @full_name, @position, @phone, @email);
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdateEmployee
    @id Char(36),
    @full_name NVARCHAR(MAX),
    @position NVARCHAR(MAX),
    @phone NVARCHAR(50),
    @email NVARCHAR(255)
AS
BEGIN
    UPDATE Employee 
    SET full_name = @full_name,
        position = @position,
        phone = @phone,
        email = @email
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_DeleteEmployee
    @id Char(36)
AS
BEGIN
    DELETE FROM Employee WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetAllEmployees
AS
BEGIN
    SELECT id, full_name, position, phone, email 
    FROM Employee;
END;
GO

-- =============================================
-- Stored Procedures for Vehicle operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_AddVehicle
    @id Char(36),
    @owner_id Char(36),
    @make NVARCHAR(100),
    @model NVARCHAR(100),
    @year INT,
    @license_plate NVARCHAR(50),
    @vin NVARCHAR(100)
AS
BEGIN
    INSERT INTO Vehicle (id, owner_id, make, model, year, license_plate, vin)
    VALUES (@id, @owner_id, @make, @model, @year, @license_plate, @vin);
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdateVehicle
    @id Char(36),
    @owner_id Char(36),
    @make NVARCHAR(100),
    @model NVARCHAR(100),
    @year INT,
    @license_plate NVARCHAR(50),
    @vin NVARCHAR(100)
AS
BEGIN
    UPDATE Vehicle 
    SET owner_id = @owner_id,
        make = @make,
        model = @model,
        year = @year,
        license_plate = @license_plate,
        vin = @vin
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_DeleteVehicle
    @id Char(36)
AS
BEGIN
    DELETE FROM Vehicle WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetAllVehicles
AS
BEGIN
    SELECT v.id, c.full_name AS owner, v.make, v.model, v.year, v.license_plate, v.vin
    FROM Vehicle v
    JOIN Client c ON v.owner_id = c.id;
END;
GO

-- =============================================
-- Stored Procedures for Policy operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_AddPolicy
    @id Char(36),
    @policy_number NVARCHAR(100),
    @client_id Char(36),
    @vehicle_id Char(36),
    @employee_id Char(36),
    @start_date DATE,
    @end_date DATE,
    @insurance_type NVARCHAR(100),
    @premium_amount DECIMAL(18,2),
    @status NVARCHAR(50)
AS
BEGIN
    INSERT INTO InsurancePolicy (id, policy_number, client_id, vehicle_id, employee_id, 
                               start_date, end_date, insurance_type, premium_amount, status)
    VALUES (@id, @policy_number, @client_id, @vehicle_id, @employee_id, 
            @start_date, @end_date, @insurance_type, @premium_amount, @status);
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdatePolicy
    @id Char(36),
    @policy_number NVARCHAR(100),
    @client_id Char(36),
    @vehicle_id Char(36),
    @employee_id Char(36),
    @start_date DATE,
    @end_date DATE,
    @insurance_type NVARCHAR(100),
    @premium_amount DECIMAL(18,2),
    @status NVARCHAR(50)
AS
BEGIN
    UPDATE InsurancePolicy 
    SET policy_number = @policy_number,
        client_id = @client_id,
        vehicle_id = @vehicle_id,
        employee_id = @employee_id,
        start_date = @start_date,
        end_date = @end_date,
        insurance_type = @insurance_type,
        premium_amount = @premium_amount,
        status = @status
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_DeletePolicy
    @id Char(36)
AS
BEGIN
    DELETE FROM InsurancePolicy WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetAllPolicies
AS
BEGIN
    SELECT 
        p.id, 
        p.policy_number, 
        c.full_name AS client, 
        v.make + ' ' + v.model AS vehicle, 
        e.full_name AS employee,
        p.start_date, 
        p.end_date, 
        p.insurance_type, 
        p.premium_amount, 
        p.status
    FROM InsurancePolicy p
    JOIN Client c ON p.client_id = c.id
    JOIN Vehicle v ON p.vehicle_id = v.id
    JOIN Employee e ON p.employee_id = e.id;
END;
GO

-- =============================================
-- Stored Procedures for Claim operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_AddClaim
    @id Char(36),
    @policy_id Char(36),
    @claim_date DATE,
    @description NVARCHAR(MAX),
    @damage_amount DECIMAL(18,2),
    @is_approved BIT
AS
BEGIN
    INSERT INTO Claim (id, policy_id, claim_date, description, damage_amount, is_approved)
    VALUES (@id, @policy_id, @claim_date, @description, @damage_amount, @is_approved);
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdateClaim
    @id Char(36),
    @policy_id Char(36),
    @claim_date DATE,
    @description NVARCHAR(MAX),
    @damage_amount DECIMAL(18,2),
    @is_approved BIT
AS
BEGIN
    UPDATE Claim 
    SET policy_id = @policy_id,
        claim_date = @claim_date,
        description = @description,
        damage_amount = @damage_amount,
        is_approved = @is_approved
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_DeleteClaim
    @id Char(36)
AS
BEGIN
    DELETE FROM Claim WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetAllClaims
AS
BEGIN
    SELECT 
        c.id, 
        p.policy_number AS policy, 
        c.claim_date, 
        c.description, 
        c.damage_amount, 
        c.is_approved
    FROM Claim c
    JOIN InsurancePolicy p ON c.policy_id = p.id;
END;
GO

-- =============================================
-- Stored Procedures for Payment operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_AddPayment
    @id Char(36),
    @claim_id Char(36),
    @payment_date DATE,
    @amount DECIMAL(18,2),
    @method NVARCHAR(100)
AS
BEGIN
    INSERT INTO Payment (id, claim_id, payment_date, amount, method)
    VALUES (@id, @claim_id, @payment_date, @amount, @method);
END;
GO

CREATE OR ALTER PROCEDURE sp_UpdatePayment
    @id Char(36),
    @claim_id Char(36),
    @payment_date DATE,
    @amount DECIMAL(18,2),
    @method NVARCHAR(100)
AS
BEGIN
    UPDATE Payment 
    SET claim_id = @claim_id,
        payment_date = @payment_date,
        amount = @amount,
        method = @method
    WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_DeletePayment
    @id Char(36)
AS
BEGIN
    DELETE FROM Payment WHERE id = @id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetAllPayments
AS
BEGIN
    SELECT 
        p.id, 
        c.description AS claim, 
        p.payment_date, 
        p.amount, 
        p.method
    FROM Payment p
    JOIN Claim c ON p.claim_id = c.id;
END;
GO

-- =============================================
-- Stored Procedures for Report operations
-- =============================================
CREATE OR ALTER PROCEDURE sp_GetActivePoliciesReport
AS
BEGIN
    SELECT 
        p.policy_number,
        c.full_name AS client,
        v.make + ' ' + v.model AS vehicle,
        p.premium_amount
    FROM InsurancePolicy p
    JOIN Client c ON p.client_id = c.id
    JOIN Vehicle v ON p.vehicle_id = v.id
    WHERE p.status = 'Active';
END;
GO

CREATE OR ALTER PROCEDURE sp_GetClaimsByMonthReport
AS
BEGIN
    SELECT 
        FORMAT(claim_date, 'yyyy-MM') AS month,
        COUNT(*) AS claim_count,
        SUM(damage_amount) AS total_damage
    FROM Claim
    GROUP BY FORMAT(claim_date, 'yyyy-MM')
    ORDER BY month;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetPaymentsSummaryReport
AS
BEGIN
    SELECT 
        p.claim_id,
        p.payment_date,
        p.amount,
        p.method
    FROM Payment p
    ORDER BY p.payment_date DESC;
END;
GO

-- =============================================
-- Stored Procedures for User authentication
-- =============================================
CREATE OR ALTER PROCEDURE sp_AuthenticateUser
    @username NVARCHAR(100),
    @password NVARCHAR(100)
AS
BEGIN
    SELECT Id, Username, Roleuser 
    FROM Users 
    WHERE Username = @username AND Password = @password;
END;
GO

-- =============================================
-- Additional useful procedures
-- =============================================
CREATE OR ALTER PROCEDURE sp_GetClientVehicles
    @client_id Char(36)
AS
BEGIN
    SELECT id, make, model, year, license_plate, vin
    FROM Vehicle
    WHERE owner_id = @client_id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetPolicyClaims
    @policy_id Char(36)
AS
BEGIN
    SELECT id, claim_date, description, damage_amount, is_approved
    FROM Claim
    WHERE policy_id = @policy_id;
END;
GO

CREATE OR ALTER PROCEDURE sp_GetClaimPayments
    @claim_id Char(36)
AS
BEGIN
    SELECT id, payment_date, amount, method
    FROM Payment
    WHERE claim_id = @claim_id;
END;
GO