USE insuranceSystem;
GO

-- 1. Active Policies View (shows all currently active insurance policies)
USE insuranceSystem;
GO

CREATE OR ALTER VIEW dbo.ActivePolicies AS
SELECT 
    p.policy_number AS [Policy ID],
    c.full_name AS [Client],
    v.make + ' ' + v.model AS [Vehicle],
    p.premium_amount AS [Premium],
    p.start_date AS [Start Date],
    p.end_date AS [End Date],
    p.status AS [Status]
FROM InsurancePolicy p
JOIN Client c ON p.client_id = c.id
JOIN Vehicle v ON p.vehicle_id = v.id
WHERE p.status = 'Active' 
AND GETDATE() BETWEEN p.start_date AND p.end_date;
GO

-- 2. Claim Payments Details View (detailed information about claims and payments)
USE insuranceSystem;
GO

CREATE OR ALTER VIEW dbo.ClaimPaymentsDetails AS
SELECT 
    FORMAT(c.claim_date, 'yyyy-MM') AS [Month],
    COUNT(*) AS [Claims Count],
    SUM(c.damage_amount) AS [Total Damage]
FROM Claim c
GROUP BY FORMAT(c.claim_date, 'yyyy-MM')
GO

-- 3. Client Claims Summary View (summary of claims by client)

CREATE OR ALTER VIEW dbo.ClientClaimsSummary AS
SELECT 
    c.id AS [Claim ID],
    p.payment_date AS [Payment Date],
    p.amount AS [Amount],
    p.method AS [Method]
FROM Claim c
JOIN Payment p ON c.id = p.claim_id;
GO