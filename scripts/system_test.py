"""End-to-end system test: backend checks, Streamlit UI walkthrough, screenshots, and video."""

from __future__ import annotations

import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "system_test" / "screenshots"
VIDEO_DIR = ROOT / "assets" / "system_test" / "video"
LOG_PATH = ROOT / "assets" / "system_test" / "TEST_LOG.txt"
APP_URL = "http://127.0.0.1:8501"

sys.path.insert(0, str(ROOT))

SHOTS.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def log(lines: list[str], message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line)
    lines.append(line)


def run_backend_checks(lines: list[str]) -> dict:
    from src.analytics import answer_question, compute_kpis, load_patients
    from src.config import ANALYTICS_DB, EXCEL_REPORT, MODEL_PATH, POWERBI_FILE, SAMPLE_CSV
    from src.excel.generate_report import generate_excel_report
    from src.ml.predict import predict_stay_risk
    from src.powerbi.launch_desktop import find_power_bi_desktop
    import pandas as pd

    results = {}
    df = load_patients()
    kpis = compute_kpis(df)
    results["patients"] = int(kpis["total_patients"])
    results["revenue"] = round(float(kpis["total_revenue"]), 2)
    results["sample_db_exists"] = ANALYTICS_DB.exists()
    results["sample_csv_exists"] = SAMPLE_CSV.exists()
    results["model_exists"] = MODEL_PATH.exists()
    results["pbix_exists"] = POWERBI_FILE.exists()
    results["pbi_exe"] = str(find_power_bi_desktop()) if find_power_bi_desktop() else None
    log(lines, f"Backend patients={results['patients']} revenue=${results['revenue']:,.2f}")

    answer = answer_question("What is total revenue by department?", df)
    results["ask_data_ok"] = "Revenue by department" in answer
    log(lines, "Ask-the-data fallback: " + ("PASS" if results["ask_data_ok"] else "FAIL"))

    scored = predict_stay_risk(
        pd.DataFrame(
            [{"Age": 62, "Gender": "Male", "MedicalCondition": "Obesity", "AdmissionType": "Emergency"}]
        )
    )
    results["stay_risk_label"] = str(scored.iloc[0]["StayRiskLabel"])
    results["stay_risk_probability"] = float(scored.iloc[0]["RiskProbability"])
    log(lines, f"Stay-risk score: {results['stay_risk_label']} ({results['stay_risk_probability']:.0%})")

    excel_path = generate_excel_report()
    results["excel_exists"] = excel_path.exists() and excel_path.stat().st_size > 0
    results["excel_path"] = str(excel_path)
    log(lines, f"Excel report: {excel_path} ({excel_path.stat().st_size} bytes)")
    results["excel_report_exists"] = EXCEL_REPORT.exists()
    return results


def wait_for_app(page, lines: list[str]) -> None:
    page.goto(APP_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("text=Hospital Operational Intelligence Portal", timeout=60000)
    # Streamlit hydrates charts after first paint.
    page.wait_for_timeout(2500)
    log(lines, f"Opened {APP_URL}")


def click_tab(page, name: str) -> None:
    tab = page.get_by_role("tab", name=name)
    if tab.count() == 0:
        tab = page.get_by_role("button", name=name)
    tab.first.click()
    page.wait_for_timeout(1500)


def shot(page, name: str, lines: list[str], full_page: bool = True) -> Path:
    path = SHOTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page)
    log(lines, f"Screenshot {path.name} ({path.stat().st_size} bytes)")
    return path


def run_ui(lines: list[str]) -> Path | None:
    video_out = VIDEO_DIR / "Medi_U_system_test.webm"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1440, "height": 900},
        )
        page = context.new_page()
        wait_for_app(page, lines)

        click_tab(page, "Overview")
        page.wait_for_timeout(1500)
        shot(page, "01_overview_kpis", lines)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(800)
        shot(page, "02_overview_charts", lines)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        shot(page, "03_overview_tables", lines)
        page.evaluate("window.scrollTo(0, 0)")

        click_tab(page, "Ask the Data")
        page.wait_for_timeout(1200)
        shot(page, "04_ask_the_data_empty", lines)
        question = "What is total revenue by department?"
        box = page.get_by_label("Ask a business question")
        if box.count() == 0:
            box = page.locator("input[type='text']").first
        box.fill(question)
        box.press("Enter")
        try:
            page.wait_for_selector("text=Revenue by department", timeout=30000)
        except PlaywrightTimeout:
            page.wait_for_timeout(4000)
        shot(page, "05_ask_the_data_answer", lines)

        click_tab(page, "Stay risk")
        page.wait_for_timeout(1500)
        shot(page, "06_stay_risk_form", lines)
        age = page.get_by_label("Age")
        if age.count():
            age.fill("74")
        gender = page.get_by_label("Gender")
        if gender.count():
            gender.select_option(index=0)
        page.get_by_role("button", name="Score stay risk").click()
        try:
            page.wait_for_selector("text=Stay risk", timeout=20000)
            page.wait_for_timeout(1500)
        except PlaywrightTimeout:
            page.wait_for_timeout(4000)
        shot(page, "07_stay_risk_result", lines)

        click_tab(page, "Reports")
        page.wait_for_timeout(1200)
        shot(page, "08_reports_idle", lines)
        page.get_by_role("button", name="Generate Excel report").click()
        try:
            page.wait_for_selector("text=Saved locally", timeout=30000)
        except PlaywrightTimeout:
            page.wait_for_timeout(5000)
        shot(page, "09_reports_generated", lines)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        shot(page, "10_reports_powerbi_help", lines)

        page.wait_for_timeout(1000)
        recorded = page.video.path() if page.video else None
        context.close()
        browser.close()

    if recorded:
        src = Path(recorded)
        if src.exists():
            shutil.move(str(src), str(video_out))
            log(lines, f"Raw video saved: {video_out}")
            return video_out
    candidates = sorted(VIDEO_DIR.glob("*.webm"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        shutil.copy2(candidates[0], video_out)
        log(lines, f"Raw video copied: {video_out}")
        return video_out
    log(lines, "WARNING: Playwright did not produce a webm video")
    return None


def transcode_mp4(webm: Path | None, lines: list[str]) -> Path | None:
    if webm is None or not webm.exists():
        return None
    mp4 = VIDEO_DIR / "Medi_U_system_test.mp4"
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        log(lines, "ffmpeg not found; leaving webm only")
        return webm
    import subprocess

    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(webm),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(mp4),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        log(lines, "ffmpeg transcode failed: " + completed.stderr[-400:])
        return webm
    log(lines, f"MP4 video saved: {mp4} ({mp4.stat().st_size} bytes)")
    return mp4


def main() -> int:
    lines: list[str] = []
    log(lines, "Medi_U full-length system test started")
    backend = run_backend_checks(lines)
    video = run_ui(lines)
    mp4 = transcode_mp4(video, lines)
    summary = {
        "started": True,
        "backend": backend,
        "screenshots": sorted(p.name for p in SHOTS.glob("*.png")),
        "video_webm": str(video) if video else None,
        "video_mp4": str(mp4) if mp4 else None,
    }
    (ROOT / "assets" / "system_test" / "TEST_RESULTS.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    log(lines, "System test complete")
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    failed = not backend.get("ask_data_ok") or not backend.get("excel_exists") or not backend.get("model_exists")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
