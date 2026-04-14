# SAP S/4HANA Finance — Key Concepts

## Universal Journal (ACDOCA)

The Universal Journal table ACDOCA is the single source of truth for all financial postings in SAP S/4HANA. It replaces the traditional tables from SAP ECC:

- **BSEG** (Accounting Document Segment) → merged into ACDOCA
- **FAGLFLEXA** (General Ledger Line Items) → merged into ACDOCA
- **COEP** (CO Line Items) → merged into ACDOCA
- **ANLP** (Asset Line Items) → merged into ACDOCA

### Key Fields in ACDOCA
| Field | Description |
|-------|-------------|
| RCLNT | Client |
| RLDNR | Ledger |
| RBUKRS | Company Code |
| GJAHR | Fiscal Year |
| BELNR | Document Number |
| BUZEI | Line Item |
| RACCT | Account Number |
| RHCUR | Local Currency Amount |
| PRCTR | Profit Center |
| SEGMENT | Segment |

### Benefits of ACDOCA
1. **Single source of truth** — no reconciliation needed between modules
2. **Real-time reporting** — no aggregate tables required
3. **Simplified data model** — fewer tables to maintain
4. **Extensibility** — custom fields via CDS views

## Business Partners

In S/4HANA, the Business Partner (BP) concept replaces the traditional Customer (KNA1) and Vendor (LFA1) master data:

- Transaction **BP** replaces XD01/XD02/XD03 (Customer) and XK01/XK02/XK03 (Vendor)
- BP roles determine the business function (Customer, Vendor, etc.)
- Customer-Vendor Integration (CVI) ensures synchronization

### Key Tables
- **BUT000** — Business Partner General Data
- **BUT020** — Business Partner Addresses
- **BUT100** — Business Partner Roles

## Material Ledger

The Material Ledger in S/4HANA is mandatory and activated by default:
- Enables actual costing
- Supports multiple currencies and valuations
- Table: **ACDOCA** with document type ML

## Fiori Launchpad

SAP Fiori is the UX framework for S/4HANA:
- **Fiori Launchpad** — central entry point for all applications
- **Fiori Apps Library** — catalog of available apps (https://fioriappslibrary.hana.ondemand.com)
- **Fiori Elements** — template-based app development

### Key Fiori Apps for Finance
| App ID | Name | Description |
|--------|------|-------------|
| F0996 | Manage Journal Entries | Create and manage journal entries |
| F2217 | Display Line Items | View financial line items |
| F1603 | Manage Fixed Assets | Asset management |
| F0814 | Cash Flow Analyzer | Cash flow analysis |

---

## SAP BAPIs for Common Operations

### Purchase Order
- **BAPI_PO_CREATE1** — Create Purchase Order
- **BAPI_PO_CHANGE** — Change Purchase Order
- **BAPI_PO_GETDETAIL1** — Get Purchase Order Details

### Sales Order
- **BAPI_SALESORDER_CREATEFROMDAT2** — Create Sales Order
- **BAPI_SALESORDER_CHANGE** — Change Sales Order
- **BAPI_SALESORDER_GETLIST** — Get Sales Order List

### Material
- **BAPI_MATERIAL_GET_ALL** — Get Material Data
- **BAPI_MATERIAL_SAVEDATA** — Create/Change Material

---

## SuccessFactors Integration

### Employee Central API
- OData API endpoint: `/odata/v2/`
- Key entities: `PerPerson`, `PerPersonal`, `EmpJob`, `EmpCompensation`
- Authentication: OAuth 2.0 with SAML Bearer Assertion

### Common Integration Scenarios
1. **Employee Master Data Sync** — EC to S/4HANA HCM
2. **Org Structure Replication** — EC to S/4HANA
3. **Payroll Integration** — EC Payroll to S/4HANA Finance

### Middleware Options
- SAP Integration Suite (CPI)
- SAP BTP Integration Suite
- Dell Boomi
- MuleSoft

---

## Hyland OnBase Integration with SAP

### Overview
OnBase integrates with SAP for document management and workflow automation:
- **Unity Integration for SAP** — embedded document access within SAP GUI
- **AP Invoice Processing** — automated invoice capture and posting
- **Archive Link** — SAP ArchiveLink protocol for document storage

### Configuration Steps
1. Configure RFC destination in SAP (SM59)
2. Set up ArchiveLink in OAC0 (content repository)
3. Define document types in OAC2
4. Configure barcode processing in OAC3
5. Link SAP business objects to OnBase document types

### Key Transactions
- **OAC0** — Define Content Repositories
- **OAC2** — Define Document Types
- **OAC3** — Configure Barcode
- **OAAD** — ArchiveLink Administration

### Integration Architecture
```
SAP S/4HANA  ←→  SAP ArchiveLink Protocol  ←→  OnBase Application Server  ←→  OnBase Disk Groups
```
