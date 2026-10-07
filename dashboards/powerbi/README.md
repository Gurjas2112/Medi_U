# Power BI — Hospital Operational Dashboard

File: `Hospital_Operational_Dashboard.pbix`

This dashboard is designed for **Power BI Desktop on Windows**. On this project machine (HSGPC) Desktop is installed from:

`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Power BI Desktop`

The executable is typically:

`C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`

## Launch

From the repository root:

```powershell
python -m src.powerbi.launch_desktop
```

or:

```powershell
.\scripts\open_powerbi.ps1
```

## Data source (refresh)

Do not point Power BI at `data/cleaned/` (those files are local-only and gitignored). Use the stable Excel extract produced by the pipeline:

1. Open Power BI Desktop.
2. **Home → Get data → Excel workbook**.
3. Select `dashboards/excel/Hospital_Operational_Report.xlsx`.
4. Load the **Patients** sheet (PascalCase columns: `PatientID`, `BillingAmount`, `LengthOfStay`, …).
5. **Home → Refresh** after each ETL run.

Optional local SQLite path after a full pipeline run: `data/sample/hospital_analytics.db`, table `Patients` (ODBC SQLite driver required).

SQL Server (optional production): `DB_SERVER` / `DB_NAME` from `.env`, table `dbo.Patients`.

## Pages

These pages match the screenshots in `assets/screenshots/`:

1. **Executive** — Total Patients, Total Revenue, Avg Billing, Avg Length of Stay.
2. **Admissions** — monthly admissions, department mix, gender.
3. **Doctor** — top doctors, patient counts, department slicer.
4. **Financial** — revenue by department, insurance coverage, billing trend.

Python does not rewrite the `.pbix` binary. The automation layer refreshes the Excel/SQLite inputs and opens Desktop against this file.
