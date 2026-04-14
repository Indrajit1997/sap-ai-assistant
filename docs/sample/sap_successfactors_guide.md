# SAP SuccessFactors — Implementation Guide

## Employee Central Configuration

### Foundation Objects (in order of setup)
1. **Country/Region** — Geographic definitions
2. **Legal Entity** — Company legal structure
3. **Business Unit** — Organizational unit
4. **Department** — Functional unit
5. **Division** — Business division
6. **Job Classification** — Job family grouping
7. **Job Code** — Specific role definition
8. **Pay Grade / Pay Range** — Compensation bands
9. **Location** — Physical locations
10. **Cost Center** — Financial tracking

### Position Management
- **Position-based** org model recommended for enterprises
- Each position has: Title, Job Code, Department, Location, Pay Grade
- Positions can be filled, vacant, or frozen
- Right-to-fill workflow for position requests

### Employee Lifecycle Events
| Event | Description | API Entity |
|-------|-------------|------------|
| Hire | New employee onboarding | `EmpJob` |
| Promotion | Role change with grade increase | `EmpJob` |
| Transfer | Department/location change | `EmpJob` |
| Termination | Employee exit | `EmpJob` with `event-reason` |

## Integration Center

### Key Features
- Visual integration designer (no-code/low-code)
- Pre-built templates for common integrations
- Support for: REST, SOAP, SFTP, OData
- Scheduling and monitoring capabilities

### Common Integration Flows
1. **EC → S/4HANA**: Employee master data replication
2. **EC → AD/Azure AD**: User provisioning
3. **EC → Payroll**: Payroll data export
4. **EC → Benefits**: Benefits enrollment data

### API Reference
```
Base URL: https://{datacenter}.successfactors.com/odata/v2/

Authentication: OAuth 2.0 SAML Bearer
Headers:
  - Authorization: Bearer {token}
  - Content-Type: application/json

Key Endpoints:
  GET /User               — User accounts
  GET /PerPerson          — Person records
  GET /EmpJob             — Job information
  GET /EmpCompensation    — Compensation data
  GET /FODepartment       — Department structure
  GET /Position           — Position catalog
```

## Performance Management

### Goal Management
- **Goal Plan Template** — defines goal structure
- **Goal Library** — pre-defined goals for selection
- **Cascading Goals** — top-down goal alignment
- **Goal Weights** — relative importance scoring

### Continuous Performance Management (CPM)
- **Activities** — track ongoing work items
- **Achievements** — record accomplishments
- **1:1 Meetings** — structured manager-employee discussions
- **Feedback** — continuous peer/manager feedback

---

## Troubleshooting Common Issues

### Issue: Employee data not syncing to S/4HANA
**Root Cause**: Usually CPI iFlow mapping errors or missing mandatory fields
**Resolution**:
1. Check Integration Center error logs
2. Verify field mapping in CPI iFlow
3. Ensure INFOTYPE mapping is correct (IT0001, IT0002, IT0006)
4. Check user permissions in both EC and S/4HANA

### Issue: OData API returning 401 Unauthorized
**Root Cause**: OAuth token expired or misconfigured
**Resolution**:
1. Regenerate SAML assertion
2. Verify API key in Provisioning → Company Settings
3. Check user permissions (role-based permissions)
4. Ensure IP allowlisting is configured

### Issue: Compound Employee API performance
**Root Cause**: Fetching too many fields without pagination
**Resolution**:
1. Use `$select` to limit fields: `?$select=userId,firstName,lastName`
2. Use `$top` and `$skip` for pagination
3. Use `$filter` to limit records: `?$filter=lastModifiedDateTime gt datetime'2024-01-01'`
4. Consider using delta tokens for incremental sync
