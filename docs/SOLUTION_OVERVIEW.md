# Medi_U solution overview

Medi_U is a hospital operational intelligence platform. It automates encounter cleaning, stay-risk scoring, Excel reporting, Power BI refresh inputs, and a Streamlit portal that works both on a local workstation and on Streamlit Community Cloud.

The Siemens Gamesa intern description (Automation / AI Intern for Blade Structural Design Process, Job ID 302765) is used only as a **skills template**: Python automation, Excel, Power BI, data analytics, AI/LLM workflow support, and traceability from requirements through verification. The product domain remains hospital operations, not wind-turbine blade design.

## Problem

Hospital leadership needs a repeatable way to:

- ingest messy encounter extracts
- publish trusted KPIs (volume, revenue, length of stay)
- flag encounters that look like **above-median stay risk**
- produce Excel and Power BI views without hand-copying tables
- ask operational questions in natural language without waiting on a new SQL ticket

## Requirements → controls → verification

| Requirement | Control in this repo | Verification |
|-------------|----------------------|--------------|
| Repeatable ingest | `src/etl/extract.py` (Kaggle or synthetic fallback) | Pipeline log + `data/raw/hospital_raw.csv` (local) |
| Clean, typed encounters | `src/etl/transform.py` (dedupe, missing values, billing > 0, length of stay) | Row counts in transform output |
| One canonical schema | PascalCase `Patients` via `src/schema.py` | SQL scripts, Excel, Power BI, Streamlit share names |
| Trusted analytics store | SQLite `data/sample/hospital_analytics.db` (and optional SQL Server) | `SELECT COUNT(*) FROM Patients` |
| Executive / admissions / doctor / financial views | Excel workbook + Power BI pages + Streamlit Overview | Screenshots in `assets/screenshots/` |
| Stay-risk scoring | Random Forest `models/stay_risk_model.pkl` | Accuracy / ROC-AUC printed at train time; Streamlit form |
| NL question answering | LLM SQL agent when configured; pandas fallback otherwise | Overview KPIs still render with no LLM |
| Hosted demo without Kaggle/SQL Server | Committed sample CSV + SQLite | `streamlit run app.py` from a fresh clone |

## Architecture

```
Kaggle or synthetic CSV
        → transform (quality rules)
        → PascalCase Patients
              ├─ SQLite / optional SQL Server
              ├─ sample extract (hostable)
              ├─ Excel operational report
              ├─ Power BI Desktop (.pbix refresh)
              ├─ stay-risk model
              └─ Streamlit portal (local or Community Cloud)
```

## Data lineage

1. **Extract** — `prasad22/healthcare-dataset` when credentials exist; otherwise Faker-based synthetic encounters with the same columns (including intentional duplicates and nulls so transform is testable offline).
2. **Transform** — duplicate removal, median/unknown fills, type coercion, invalid billing dropped, age bands, length of stay, calendar fields, `PatientID`.
3. **Load** — columns renamed to PascalCase (`BillingAmount`, `LengthOfStay`, …), loaded to `Patients`. A 1,500-row sample is written to `data/sample/` for GitHub and Streamlit Cloud. Full local copies stay under `data/cleaned/` and are gitignored.
4. **Consume** — Streamlit, Excel, Power BI, `sql/analysis.sql`, and `notebooks/eda.ipynb`.

## Components

### ETL

`python -m src.etl.pipeline` runs extract, transform, load, Excel generation, and model training. `scripts/run_etl.py` is a root-level wrapper.

### Excel automation

`src/excel/generate_report.py` writes `dashboards/excel/Hospital_Operational_Report.xlsx`:

- Executive KPIs and department table + bar chart
- Admissions monthly trend
- Doctors ranking
- Financial insurance mix
- Patients extract (Power BI source sheet)

The Streamlit **Reports** tab can regenerate and download the same workbook.

### Power BI

`dashboards/powerbi/Hospital_Operational_Dashboard.pbix` is opened locally by `src/powerbi/launch_desktop.py`, which looks for `PBIDesktop.exe` and the Start Menu folder on HSGPC. Python does not author DAX inside the binary; it keeps the Excel/SQLite inputs stable and launches Desktop.

### Machine learning

Target: **IsLongStay** = length of stay above the dataset median. Features: Age, Gender, MedicalCondition, AdmissionType. Artifact: `models/stay_risk_model.pkl`. This is an operational burden signal, not a clinical diagnostic.

### AI assistant

`src/rag/chatbot.py` tries Ollama (`USE_OLLAMA=1`) or OpenAI (`OPENAI_API_KEY`). If neither is available — the Streamlit Cloud default — `src/analytics.answer_question` answers KPI-style questions from pandas so the hosted app never depends on a local LLM.

## Skills mapping (intern JD used as reference only)

| Skill called out in the intern role | How Medi_U demonstrates it |
|-------------------------------------|----------------------------|
| Python automation | ETL pipeline, Excel writer, Power BI launcher |
| Excel automation | Multi-sheet formatted workbook with charts |
| Power BI | Four-page desktop dashboard + refresh contract |
| Data analytics | KPIs, department/doctor/insurance views, SQL analysis |
| AI / LLM evaluation | Optional SQL agent + deterministic fallback |
| Engineering workflow / traceability | Requirements table above; one schema across tools |
| Risk assessment templates | Long-stay risk model and scored labels |

## Limitations

- Power BI Service publishing needs a Microsoft work tenant; this repo automates Desktop only.
- The sample dataset is synthetic or sampled public healthcare columns, not a live hospital EHR.
- Stay-risk is a statistical median split, not a clinically validated model.
- Streamlit Cloud cannot run Ollama, SQL Server, or Power BI Desktop.
