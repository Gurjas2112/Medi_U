# Medi_U — Hospital Operational Intelligence

Python automation for hospital encounter analytics: ETL, a stay-risk model, Excel reporting, Power BI Desktop refresh, and a Streamlit portal that also runs on Streamlit Community Cloud.

Code host: [https://github.com/Gurjas2112/Medi_U](https://github.com/Gurjas2112/Medi_U)

App host: Streamlit Community Cloud — deploy from `main` with Main file `app.py` (see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)). After you connect the repo at [share.streamlit.io](https://share.streamlit.io), the public URL is `https://<app-name>.streamlit.app`.

## What you can do

- Run a full **extract → transform → load** pipeline (Kaggle or offline synthetic data).
- Publish a canonical **PascalCase `Patients`** table to SQLite (default) or SQL Server.
- Open a four-page **Power BI** dashboard on this Windows PC.
- Generate **`Hospital_Operational_Report.xlsx`** (Executive, Admissions, Doctors, Financial, Patients).
- Score **above-median length-of-stay risk** from Age, Gender, Medical Condition, and Admission Type.
- Ask operational questions in Streamlit. If no LLM is configured, built-in analytics still answer.

This repository stays in the **hospital** domain. The intern role description for blade structural design was used only as a skills checklist (Python, Excel, Power BI, AI, automation, traceability). Details: [docs/SOLUTION_OVERVIEW.md](docs/SOLUTION_OVERVIEW.md). This machine: [docs/SYSTEM_SPEC.md](docs/SYSTEM_SPEC.md).

## Architecture

```
extract → transform → PascalCase Patients
                         ├─ SQLite sample (GitHub + Streamlit Cloud)
                         ├─ Excel workbook
                         ├─ Power BI Desktop
                         ├─ stay-risk model
                         └─ Streamlit (Overview / Ask / Risk / Reports)
```

## Repository layout

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit entry (required at repo root for Community Cloud) |
| `src/config.py` | Paths and schema map |
| `src/etl/` | Extract, transform, load, pipeline |
| `src/excel/` | Operational workbook generator |
| `src/powerbi/` | Desktop launcher for HSGPC |
| `src/ml/` | Train / predict stay risk |
| `src/rag/` | Optional LLM SQL agent + fallback |
| `src/analytics.py` | KPIs and deterministic Q&A |
| `data/sample/` | Committed SQLite + CSV used by the hosted app |
| `dashboards/powerbi/` | `Hospital_Operational_Dashboard.pbix` |
| `dashboards/excel/` | Generated Excel report |
| `sql/` | `HospitalDB` DDL and 18 analysis queries |
| `notebooks/eda.ipynb` | EDA on the sample extract |
| `assets/screenshots/` | Executive, Admissions, Doctor, Financial pages |
| `docs/` | System spec, solution overview, deployment |
| `scripts/` | `run_etl.py`, `open_powerbi.ps1` |

## Local setup (Windows 11, Python 3.12)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-local.txt
copy .env.example .env
python -m src.etl.pipeline
streamlit run app.py
```

Runtime-only (no Kaggle / SQL Server / Ollama extras):

```powershell
pip install -r requirements.txt
streamlit run app.py
```

### Excel and Power BI

```powershell
python -m src.excel.generate_report
python -m src.powerbi.launch_desktop
```

Power BI Desktop on this PC is installed from `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Power BI Desktop`. Refresh from the **Patients** sheet in `dashboards/excel/Hospital_Operational_Report.xlsx`. More: [dashboards/powerbi/README.md](dashboards/powerbi/README.md).

### Optional AI

- Local: install Ollama, `ollama pull llama3.2:latest`, set `USE_OLLAMA=1` in `.env`.
- Cloud: add `OPENAI_API_KEY` in Streamlit secrets.

Without either, **Ask the Data** still answers volume, revenue, stay, department, doctor, insurance, and trend questions.

## Streamlit Cloud

1. Push `main` to GitHub.
2. [share.streamlit.io](https://share.streamlit.io) → New app → `Gurjas2112/Medi_U` → branch `main` → Main file `app.py` → Python 3.12.
3. Deploy. Optional secrets: `OPENAI_API_KEY`.

Use `requirements.txt` in Cloud, not `requirements-local.txt` (`pyodbc` is not available there).

## Skills demonstrated

Python ETL, Excel automation (openpyxl), Power BI Desktop integration, SQLite/SQL Server, scikit-learn risk scoring, Streamlit dashboards, optional LLM-over-SQL, and documented lineage from ingest rules to verification outputs.
