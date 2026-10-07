# System specification — HSGPC

This document records the workstation used to develop, run, and refresh Medi_U locally. Streamlit Community Cloud does **not** use this GPU or Power BI Desktop; those remain local.

## Hardware

| Item | Value |
|------|--------|
| Device name | HSGPC |
| Processor | 11th Gen Intel(R) Core(TM) i7-11800H @ 2.30 GHz |
| Installed RAM | 16.0 GB (15.7 GB usable) |
| Discrete GPU | NVIDIA GeForce RTX 3060 Laptop GPU (6 GB) |
| Integrated graphics | Intel(R) UHD Graphics (128 MB) |
| Storage | 954 GB total (~598 GB used at capture time) |
| Device ID | F80032BC-31A6-4FF2-AC0C-BA1ECA2CA634 |
| Product ID | 00325-82262-18452-AAOEM |
| System type | 64-bit operating system, x64-based processor |
| Pen and touch | Not available |

The stay-risk model is scikit-learn Random Forest on CPU. CUDA is available on this machine but is **not** required for Medi_U.

## Operating system

| Item | Value |
|------|--------|
| Edition | Windows 11 Home |
| Version | 26H2 |
| OS build | 26300.9550 |
| Experience pack | Windows Feature Experience Pack 1000.26100.372.0 |
| Installed on | 11-11-2024 |
| Kernel string | Microsoft Windows [Version 10.0.26300.9550] |

## Software used by this solution

| Tool | Version / location | Role |
|------|--------------------|------|
| Python | 3.12.0 (`python --version`) | ETL, Excel automation, ML, Streamlit |
| CUDA toolkit | 13.2 (nvcc V13.2.78, built 19 Mar 2026) | Present on HSGPC; unused by the Random Forest pipeline |
| Power BI Desktop | Start Menu `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Power BI Desktop` | Local four-page operational dashboard |
| Expected PBI exe | `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe` | Opened by `python -m src.powerbi.launch_desktop` |
| Git | Git for Windows / Git Bash | Commit and push to `main` |
| Optional local LLM | Ollama + `llama3.2:latest` at `http://localhost:11434` | SQL agent in Streamlit when `USE_OLLAMA=1` |
| Optional production DB | Microsoft SQL Server + ODBC Driver 17 | `DB_ENGINE=sqlserver` |

## What runs where

| Capability | HSGPC (this PC) | Streamlit Community Cloud |
|------------|-----------------|---------------------------|
| Sample SQLite + KPI dashboard | Yes | Yes |
| Excel report generate/download | Yes | Yes |
| Stay-risk prediction | Yes | Yes (committed `models/stay_risk_model.pkl`) |
| Full ETL + Kaggle/synthetic extract | Yes (`requirements-local.txt`) | No (uses committed sample) |
| Power BI Desktop | Yes | No |
| SQL Server | Optional | No |
| Ollama | Optional | No |
| OpenAI SQL agent | Optional | Optional via Streamlit secrets |

## Recommended local runtime

```powershell
python --version          # 3.12.0
pip install -r requirements-local.txt
copy .env.example .env
python -m src.etl.pipeline
streamlit run app.py
python -m src.powerbi.launch_desktop
```
