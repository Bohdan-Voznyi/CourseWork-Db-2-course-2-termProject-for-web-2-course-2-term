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
CREATE OR ALTER VIEW dbo.ClaimPaymentsDetails AS
SELECT 
    cl.id AS ClaimId,
    p.policy_number AS PolicyNumber,
    c.full_name AS ClientName,
    v.make + ' ' + v.model AS Vehicle,
    cl.claim_date AS ClaimDate,
    cl.description AS ClaimDescription,
    cl.damage_amount AS DamageAmount,
    CASE WHEN cl.is_approved = 1 THEN 'Approved' ELSE 'Pending' END AS ClaimStatus,
    py.id AS PaymentId,
    py.payment_date AS PaymentDate,
    py.amount AS PaymentAmount,
    py.method AS PaymentMethod,
    e.full_name AS ProcessedBy
FROM Claim cl
JOIN InsurancePolicy p ON cl.policy_id = p.id
JOIN Client c ON p.client_id = c.id
JOIN Vehicle v ON p.vehicle_id = v.id
LEFT JOIN Payment py ON py.claim_id = cl.id
LEFT JOIN Employee e ON p.employee_id = e.id;
GO

-- 3. Client Claims Summary View (summary of claims by client)
CREATE OR ALTER VIEW dbo.ClientClaimsSummary AS
SELECT 
    c.id AS ClientId,
    c.full_name AS ClientName,
    COUNT(cl.id) AS TotalClaims,
    SUM(CASE WHEN cl.is_approved = 1 THEN 1 ELSE 0 END) AS ApprovedClaims,
    SUM(CASE WHEN cl.is_approved = 0 THEN 1 ELSE 0 END) AS PendingClaims,
    SUM(cl.damage_amount) AS TotalDamageAmount,
    SUM(py.amount) AS TotalPayments,
    MAX(cl.claim_date) AS LastClaimDate
FROM Client c
LEFT JOIN InsurancePolicy p ON p.client_id = c.id
LEFT JOIN Claim cl ON cl.policy_id = p.id
LEFT JOIN Payment py ON py.claim_id = cl.id
GROUP BY c.id, c.full_name;
GO