USE insuranceSystem;
GO

-- Clear all tables first (in reverse order of creation to respect foreign keys)
DELETE FROM Payment;
DELETE FROM Claim;
DELETE FROM InsurancePolicy;
DELETE FROM Vehicle;
DELETE FROM Client;
DELETE FROM Employee;
GO

-- Insert 5 Employees (parent table)
INSERT INTO Employee (id, full_name, position, phone, email)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'John Smith', 'Insurance Agent', '+380501234567', 'john.smith@insurance.com'),
    ('22222222-2222-2222-2222-222222222222', 'Emily Johnson', 'Claims Adjuster', '+380502345678', 'emily.j@insurance.com'),
    ('33333333-3333-3333-3333-333333333333', 'Michael Brown', 'Sales Manager', '+380503456789', 'michael.b@insurance.com'),
    ('44444444-4444-4444-4444-444444444444', 'Sarah Wilson', 'Customer Service', '+380504567890', 'sarah.w@insurance.com'),
    ('55555555-5555-5555-5555-555555555555', 'David Lee', 'Underwriter', '+380505678901', 'david.l@insurance.com');
GO

-- Insert 5 Clients (parent table)
INSERT INTO Client (id, full_name, address, phone, email, passport_number)
VALUES 
    ('66666666-6666-6666-6666-666666666666', 'Ivan Petrenko', 'Kyiv, Khreshchatyk 1', '+380671234567', 'ivan.p@gmail.com', 'AA123456'),
    ('77777777-7777-7777-7777-777777777777', 'Olena Kovalenko', 'Lviv, Rynok Square 5', '+380672345678', 'olena.k@gmail.com', 'AB234567'),
    ('88888888-8888-8888-8888-888888888888', 'Mykhailo Shevchenko', 'Odesa, Deribasivska 10', '+380673456789', 'mykhailo.s@gmail.com', 'AC345678'),
    ('99999999-9999-9999-9999-999999999999', 'Natalia Boyko', 'Kharkiv, Sumska 20', '+380674567890', 'natalia.b@gmail.com', 'AD456789'),
    ('00000000-0000-0000-0000-000000000000', 'Andriy Melnyk', 'Dnipro, Soborna 15', '+380675678901', 'andriy.m@gmail.com', 'AE567890');
GO

-- Insert 5 Vehicles (child of Client)
INSERT INTO Vehicle (id, owner_id, make, model, year, license_plate, vin)
VALUES 
    ('11111111-1111-1111-1111-111111111112', '66666666-6666-6666-6666-666666666666', 'Toyota', 'Camry', 2018, 'AA1234BB', 'JT2BF22K8W0123456'),
    ('22222222-2222-2222-2222-222222222223', '77777777-7777-7777-7777-777777777777', 'Honda', 'CR-V', 2020, 'BC5678DE', '5J6RW1H85NL012345'),
    ('33333333-3333-3333-3333-333333333334', '88888888-8888-8888-8888-888888888888', 'Volkswagen', 'Golf', 2019, 'CE9012FK', 'WVWZZZ1KZ9W012345'),
    ('44444444-4444-4444-4444-444444444445', '99999999-9999-9999-9999-999999999999', 'BMW', 'X5', 2021, 'KA3456LM', 'WBXPC91040B012345'),
    ('55555555-5555-5555-5555-555555555556', '00000000-0000-0000-0000-000000000000', 'Skoda', 'Octavia', 2017, 'OP7890QR', 'TMBJJ7NU3J7012345');
GO

-- Insert 5 Insurance Policies (child of Client, Vehicle, and Employee)
INSERT INTO InsurancePolicy (id, policy_number, client_id, vehicle_id, employee_id, start_date, end_date, insurance_type, premium_amount, status)
VALUES 
    ('11111111-1111-1111-1111-111111111113', 'POL-2023-001', '66666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111112', '11111111-1111-1111-1111-111111111111', '2023-01-01', '2024-01-01', 'Full Coverage', 1200.00, 'Active'),
    ('22222222-2222-2222-2222-222222222224', 'POL-2023-002', '77777777-7777-7777-7777-777777777777', '22222222-2222-2222-2222-222222222223', '22222222-2222-2222-2222-222222222222', '2023-02-15', '2024-02-15', 'Third Party', 800.50, 'Active'),
    ('33333333-3333-3333-3333-333333333335', 'POL-2023-003', '88888888-8888-8888-8888-888888888888', '33333333-3333-3333-3333-333333333334', '33333333-3333-3333-3333-333333333333', '2023-03-10', '2024-03-10', 'Full Coverage', 950.75, 'Active'),
    ('44444444-4444-4444-4444-444444444446', 'POL-2023-004', '99999999-9999-9999-9999-999999999999', '44444444-4444-4444-4444-444444444445', '44444444-4444-4444-4444-444444444444', '2023-04-20', '2024-04-20', 'Comprehensive', 1500.00, 'Active'),
    ('55555555-5555-5555-5555-555555555557', 'POL-2023-005', '00000000-0000-0000-0000-000000000000', '55555555-5555-5555-5555-555555555556', '55555555-5555-5555-5555-555555555555', '2023-05-05', '2024-05-05', 'Third Party', 700.25, 'Active');
GO

-- Insert 5 Claims (child of InsurancePolicy)
INSERT INTO Claim (id, policy_id, claim_date, description, damage_amount, is_approved)
VALUES 
    ('11111111-1111-1111-1111-111111111114', '11111111-1111-1111-1111-111111111113', '2023-06-15', 'Rear-end collision', 2500.00, 1),
    ('22222222-2222-2222-2222-222222222225', '22222222-2222-2222-2222-222222222224', '2023-07-20', 'Side mirror damage', 500.00, 1),
    ('33333333-3333-3333-3333-333333333336', '33333333-3333-3333-3333-333333333335', '2023-08-10', 'Windshield crack', 800.00, 0),
    ('44444444-4444-4444-4444-444444444447', '44444444-4444-4444-4444-444444444446', '2023-09-05', 'Theft of vehicle', 25000.00, 1),
    ('55555555-5555-5555-5555-555555555558', '55555555-5555-5555-5555-555555555557', '2023-10-12', 'Parking lot scratch', 300.00, 0);
GO

-- Insert 5 Payments (child of Claim)
INSERT INTO Payment (id, claim_id, payment_date, amount, method)
VALUES 
    ('11111111-1111-1111-1111-111111111115', '11111111-1111-1111-1111-111111111114', '2023-06-30', 2500.00, 'Bank Transfer'),
    ('22222222-2222-2222-2222-222222222226', '22222222-2222-2222-2222-222222222225', '2023-07-25', 500.00, 'Credit Card'),
    ('33333333-3333-3333-3333-333333333337', '44444444-4444-4444-4444-444444444447', '2023-09-15', 25000.00, 'Bank Transfer'),
    ('44444444-4444-4444-4444-444444444448', '11111111-1111-1111-1111-111111111114', '2023-07-05', 500.00, 'Bank Transfer'),
    ('55555555-5555-5555-5555-555555555559', '22222222-2222-2222-2222-222222222225', '2023-08-01', 200.00, 'Credit Card');
GO

-- Verify counts
SELECT 
    (SELECT COUNT(*) FROM Employee) AS EmployeeCount,
    (SELECT COUNT(*) FROM Client) AS ClientCount,
    (SELECT COUNT(*) FROM Vehicle) AS VehicleCount,
    (SELECT COUNT(*) FROM InsurancePolicy) AS PolicyCount,
    (SELECT COUNT(*) FROM Claim) AS ClaimCount,
    (SELECT COUNT(*) FROM Payment) AS PaymentCount;
GO