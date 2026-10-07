"""Streamlit entry point for the Hospital Operational Intelligence Portal."""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from src.analytics import (
    compute_kpis,
    condition_breakdown,
    department_performance,
    gender_breakdown,
    insurance_breakdown,
    load_patients,
    monthly_admissions,
    top_doctors,
)
from src.excel.generate_report import generate_excel_report
from src.ml.predict import load_model, predict_stay_risk
from src.rag.chatbot import ask_hospital_ai

st.set_page_config(page_title="Medi_U Hospital Intelligence", page_icon="🏥", layout="wide")


@st.cache_data(show_spinner=False)
def get_patients() -> pd.DataFrame:
    return load_patients()


@st.cache_resource(show_spinner=False)
def get_model_artifact():
    try:
        return load_model()
    except FileNotFoundError:
        return None


def _fmt_currency(value: float) -> str:
    return f"${value:,.0f}"


df = get_patients()
kpis = compute_kpis(df)
model_artifact = get_model_artifact()

st.title("Hospital Operational Intelligence Portal")
st.caption("Medi_U — analytics, stay-risk scoring, Excel automation, and an AI data assistant.")

overview, ask, risk, reports = st.tabs(
    ["Overview", "Ask the Data", "Stay risk", "Reports"]
)

with overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patients", f"{kpis['total_patients']:,}")
    c2.metric("Total revenue", _fmt_currency(kpis["total_revenue"]))
    c3.metric("Avg billing", _fmt_currency(kpis["avg_billing"]))
    c4.metric("Avg length of stay", f"{kpis['avg_length_of_stay']:.1f} days")

    left, right = st.columns(2)
    dept = department_performance(df)
    monthly = monthly_admissions(df)
    with left:
        st.subheader("Revenue by department")
        st.bar_chart(dept.set_index("Department")["TotalRevenue"])
        st.dataframe(dept, hide_index=True, use_container_width=True)
    with right:
        st.subheader("Monthly admissions")
        st.line_chart(monthly.set_index("Period")["Admissions"])
        st.subheader("Insurance mix")
        st.bar_chart(insurance_breakdown(df).set_index("InsuranceProvider")["PatientCount"])

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        st.subheader("Top doctors")
        st.dataframe(top_doctors(df), hide_index=True, use_container_width=True)
    with bottom_right:
        st.subheader("Conditions and gender")
        st.dataframe(condition_breakdown(df), hide_index=True, use_container_width=True)
        st.dataframe(gender_breakdown(df), hide_index=True, use_container_width=True)

with ask:
    st.subheader("Talk to the hospital dataset")
    st.caption(
        "Uses a local Ollama model or OpenAI when configured. Otherwise answers come from "
        "built-in SQL/pandas analytics so the hosted demo always works."
    )
    user_query = st.text_input(
        "Ask a business question",
        placeholder="e.g. What is total revenue by department?",
    )
    if user_query:
        with st.spinner("Analyzing records..."):
            answer = ask_hospital_ai(user_query)
        st.info(answer)
    else:
        st.write("Try questions about KPIs, departments, doctors, insurance, conditions, or monthly trends.")

with risk:
    st.subheader("Predict above-median length of stay")
    if model_artifact is None:
        st.warning("Stay-risk model not found. Run `python -m src.etl.pipeline` to train it.")
    else:
        categories = model_artifact.get("categories", {})
        genders = categories.get("Gender") or sorted(df["Gender"].dropna().unique().tolist())
        conditions = categories.get("MedicalCondition") or sorted(
            df["MedicalCondition"].dropna().unique().tolist()
        )
        admission_types = categories.get("AdmissionType") or sorted(
            df["AdmissionType"].dropna().unique().tolist()
        )
        with st.form("stay_risk_form"):
            age = st.number_input("Age", min_value=0, max_value=120, value=62)
            gender = st.selectbox("Gender", genders)
            condition = st.selectbox("Medical condition", conditions)
            admission_type = st.selectbox("Admission type", admission_types)
            submitted = st.form_submit_button("Score stay risk")
        if submitted:
            scored = predict_stay_risk(
                pd.DataFrame(
                    [
                        {
                            "Age": age,
                            "Gender": gender,
                            "MedicalCondition": condition,
                            "AdmissionType": admission_type,
                        }
                    ]
                )
            )
            row = scored.iloc[0]
            st.metric("Stay risk", row["StayRiskLabel"], delta=f"{row['RiskProbability']:.0%} probability")
            st.caption(
                "High stay risk means the model estimates a length of stay above the dataset median."
            )

with reports:
    st.subheader("Excel operational report")
    st.write(
        "The workbook mirrors the Power BI pages: Executive, Admissions, Doctors, Financial, and Patients."
    )
    if st.button("Generate Excel report"):
        report_path = generate_excel_report()
        st.success(f"Saved locally to {report_path}")
        buffer = BytesIO()
        with report_path.open("rb") as handle:
            buffer.write(handle.read())
        buffer.seek(0)
        st.download_button(
            "Download Hospital_Operational_Report.xlsx",
            data=buffer,
            file_name="Hospital_Operational_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    st.markdown(
        """
Local Power BI Desktop:

```powershell
python -m src.powerbi.launch_desktop
```

Or run `scripts/open_powerbi.ps1`. Refresh the `Patients` sheet from
`dashboards/excel/Hospital_Operational_Report.xlsx`.
"""
    )
