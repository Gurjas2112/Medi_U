# Deployment

## Local (HSGPC)

Python 3.12.0, Windows 11 26H2.

```powershell
cd "C:\Users\Gurjas Gandhi\OneDrive\Desktop\Medi_U"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-local.txt
copy .env.example .env
python -m src.etl.pipeline
streamlit run app.py
```

The app is at [http://localhost:8501](http://localhost:8501).

### Excel

```powershell
python -m src.excel.generate_report
```

Output: `dashboards/excel/Hospital_Operational_Report.xlsx`.

### Power BI Desktop

```powershell
python -m src.powerbi.launch_desktop
```

or Git Bash / PowerShell:

```powershell
./scripts/open_powerbi.ps1
```

Refresh data from the **Patients** sheet in the Excel workbook.

### Optional local LLM

Install Ollama, then:

```powershell
ollama pull llama3.2:latest
```

Set `USE_OLLAMA=1` in `.env` and restart Streamlit.

### Optional SQL Server

Set `DB_ENGINE=sqlserver` and the `DB_*` values in `.env`. Run `sql/create_tables.sql` only if you want the DDL without pandas; `load_sql.py` will also create `Patients` via `to_sql`.

## GitHub (code host)

Remote: `https://github.com/Gurjas2112/Medi_U`

Branch: `main`

The committed tree includes source, docs, sample SQLite/CSV, the stay-risk pickle, Power BI file, screenshots, and the generated Excel report. Raw/full cleaned dumps stay gitignored.

## Streamlit Community Cloud (app host)

1. Push `main` to GitHub (already the project remote).
2. Sign in at [https://share.streamlit.io](https://share.streamlit.io) with the same GitHub account (`Gurjas2112`).
3. **New app**:
   - Repository: `Gurjas2112/Medi_U`
   - Branch: `main`
   - Main file path: `app.py`
   - Python version: 3.12
4. (Optional) App settings → Secrets:

```
OPENAI_API_KEY = "..."
OPENAI_MODEL = "gpt-4o-mini"
USE_OLLAMA = "0"
```

5. Deploy. The public URL will look like `https://<app-name>.streamlit.app`.

`requirements.txt` is Streamlit-safe (no `pyodbc`). Do not point Cloud at `requirements-local.txt`.

The hosted app reads `data/sample/hospital_analytics.db` and `models/stay_risk_model.pkl`. It does not download Kaggle data and does not open Power BI.

## Smoke checks after deploy

- Overview KPIs render without an API key.
- Ask the Data answers “What is total revenue by department?” via the pandas fallback.
- Stay risk form returns a label and probability.
- Reports tab downloads an `.xlsx` file.
