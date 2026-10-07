# Medi_U full-length system test report

**Date:** 7 October 2026  
**Workstation:** HSGPC (Windows 11 26H2, Python 3.12, Power BI Desktop, Excel)  
**Purpose:** Exercise the hospital intelligence platform end-to-end against the intern JD skill set (Job ID 302765 used as a skills template only; domain remains hospital operations).

## Evidence pack

| Artifact | Path |
|----------|------|
| Walkthrough video | `assets/system_test/video/Medi_U_Full_System_Test.mp4` |
| Flow screenshots | `assets/system_test/screenshots/` |
| Backend log | `assets/system_test/logs/backend_system_test.log` |
| This report | `assets/system_test/TEST_REPORT.md` |

## Result

**Backend automated checks: 10/10 PASS.**

Streamlit UI, Excel Desktop, and Power BI Desktop were exercised live. One Excel overwrite failed while the workbook was open (file lock); the generator now writes `Hospital_Operational_Report_latest.xlsx` in that case.

## Flow-wise screenshots

| File | Flow | JD skill |
|------|------|----------|
| `02_streamlit_overview.png` | KPI portal: 1,500 patients, $37.7M revenue, $25,157 avg billing, 15.6 day stay | Python dashboards, data analytics |
| `03_ask_the_data.png` | NL question “What is total revenue by department?” answered by analytics/AI fallback | AI / LLM / knowledge workflow |
| `04_stay_risk_form.png` | Age / gender / condition / admission-type scoring form | Risk-assessment template |
| `05_stay_risk_result.png` | **High stay risk**, 93% probability | Risk scoring / ML |
| `06_reports_excel.png` | Streamlit Reports tab (Excel + Power BI launch instructions) | Digital engineering tool |
| `06_reports_file_lock.png` | File-lock while Excel had the workbook open | Verification / control |
| `07_excel_desktop.png` | Excel Executive sheet with KPI row, department table, bar chart, five tabs | Excel automation |
| `10_powerbi_executive.png` | Power BI Executive page | Power BI dashboard |
| `11_powerbi_admissions.png` | Power BI Admissions page | Power BI dashboard |
| `12_powerbi_doctor.png` | Power BI Doctor page | Power BI dashboard |
| `13_powerbi_financial.png` | Power BI Financial page | Power BI dashboard |
| `09_backend_pass.png` | SQLite + Excel + ML + AI + PBI discovery log | Traceability / verification |

Power BI Desktop was also opened on HSGPC (`Hospital_Operational_Dashboard`) with pages **Executive, Admissions, Financial, Doctors** and fields `DateTable` / `hospital_cleaned`.

## Backend checks (all PASS)

1. Load 1,500-row PascalCase `Patients` sample  
2. KPI computation (volume, revenue, stay)  
3. SQLite `hospital_analytics.db` (`BillingAmount`, `LengthOfStay`)  
4. Hostable sample CSV present  
5. Excel workbook sheets: Executive, Admissions, Doctors, Financial, Patients  
6. Stay-risk model scores an encounter  
7. AI/analytics Q&A returns department revenue  
8. Executive summary Q&A  
9. Power BI Desktop executable discovered  
10. Excel/Power BI artifacts present  

## JD coverage matrix

| JD expectation | How this test satisfied it |
|----------------|----------------------------|
| Automation for risk assessment / compliance-style workflow | Stay-risk form + Random Forest score + logged probability |
| Dashboards with Python, data analytics, AI | Streamlit Overview KPIs/charts + Ask the Data |
| Traceability: requirements → data → controls → verification | Canonical PascalCase schema, SQLite count, this report |
| Evaluate AI / LLM for knowledge and workflow | NL question answered without a live LLM (deterministic fallback); optional Ollama/OpenAI path remains |
| Python | ETL modules, analytics, ML, Streamlit, Excel writer, PBI launcher |
| Excel automation | `Hospital_Operational_Report.xlsx` with KPIs, tables, chart, five sheets |
| Power BI | Desktop opened; four pages evidenced |
| Databases | SQLite `Patients` (SQL Server remains optional) |
| Digital tool development | Streamlit portal + Excel download + PBI launch script |

Not in scope for this product (and not faked): MATLAB, Power BI Service tenant publish, clinical validation of the stay-risk model.

## Finding and fix

Generating the Excel report from Streamlit while Excel had `Hospital_Operational_Report.xlsx` open raised `PermissionError`. `src/excel/generate_report.py` now writes `Hospital_Operational_Report_latest.xlsx` when the primary file is locked.
