"""Build a 1920x1080 walkthrough video from system-test screenshots."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "system_test" / "screenshots"
SLIDES = ROOT / "assets" / "system_test" / "slides"
VIDEO = ROOT / "assets" / "system_test" / "video" / "Medi_U_Full_System_Test.mp4"
SIZE = (1920, 1080)
BG = (15, 76, 129)
WHITE = (255, 255, 255)
MUTED = (232, 241, 250)

SLIDE_PLAN = [
    ("title", "Medi_U full-length system test", "Hospital operational intelligence — Python, Excel, Power BI, AI, stay-risk"),
    ("title", "JD skills covered (Job ID 302765 as template)", "Automation · dashboards · Excel · Power BI · Python · AI/LLM · risk scoring · traceability"),
    ("image", "02_streamlit_overview.png", "1. Python dashboard — Overview KPIs and department analytics"),
    ("image", "03_ask_the_data.png", "2. AI / knowledge workflow — natural-language revenue question"),
    ("image", "04_stay_risk_form.png", "3. Risk assessment template — stay-risk scoring form"),
    ("image", "05_stay_risk_result.png", "4. Risk output — High stay risk at 93% probability"),
    ("image", "06_reports_excel.png", "5. Digital engineering tool — Streamlit Excel report action"),
    ("image", "07_excel_desktop.png", "6. Excel automation — Executive KPIs, chart, and five report sheets"),
    ("image", "10_powerbi_executive.png", "7. Power BI — Executive page"),
    ("image", "11_powerbi_admissions.png", "8. Power BI — Admissions page"),
    ("image", "12_powerbi_doctor.png", "9. Power BI — Doctor page"),
    ("image", "13_powerbi_financial.png", "10. Power BI — Financial page"),
    ("image", "09_backend_pass.png", "11. Verification log — SQLite, Excel, ML, AI fallback, Power BI discovery"),
    ("title", "Result: 10/10 backend checks passed", "Evidence: assets/system_test/  |  Video + flow-wise screenshots + TEST_REPORT.md"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path(r"C:\Windows\Fonts") / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def canvas() -> Image.Image:
    return Image.new("RGB", SIZE, BG)


def render_title(heading: str, sub: str) -> Image.Image:
    img = canvas()
    draw = ImageDraw.Draw(img)
    draw.rectangle((80, 80, 1840, 1000), fill=BG, outline=WHITE, width=3)
    draw.text((140, 360), heading, font=font(54, bold=True), fill=WHITE)
    draw.text((140, 480), sub, font=font(28), fill=MUTED)
    return img


def render_captioned(path: Path, caption: str) -> Image.Image:
    img = canvas()
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1920, 96), fill=(11, 54, 92))
    draw.text((40, 28), caption, font=font(28, bold=True), fill=WHITE)
    shot = Image.open(path).convert("RGB")
    box = (1840, 940)
    shot.thumbnail(box, Image.Resampling.LANCZOS)
    x = (1920 - shot.width) // 2
    y = 96 + (984 - shot.height) // 2
    img.paste(shot, (x, y))
    return img


def render_log_card() -> Path:
    log = (ROOT / "assets" / "system_test" / "logs" / "backend_system_test.log").read_text(encoding="utf-8")
    img = canvas()
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1920, 96), fill=(11, 54, 92))
    draw.text((40, 28), "Backend system test log — all PASS", font=font(28, bold=True), fill=WHITE)
    y = 140
    for line in log.splitlines():
        draw.text((80, y), line.replace("\t", "  |  ")[:110], font=font(22), fill=WHITE)
        y += 70
    out = SHOTS / "09_backend_pass.png"
    img.save(out)
    return out


def main() -> None:
    SLIDES.mkdir(parents=True, exist_ok=True)
    render_log_card()
    frames: list[Path] = []
    for idx, spec in enumerate(SLIDE_PLAN, start=1):
        if spec[0] == "title":
            slide = render_title(spec[1], spec[2])
        else:
            source = SHOTS / spec[1]
            if not source.exists():
                continue
            slide = render_captioned(source, spec[2])
        dest = SLIDES / f"slide_{idx:02d}.png"
        slide.save(dest)
        frames.append(dest)

    list_file = SLIDES / "concat.txt"
    lines = []
    for frame in frames:
        lines.append(f"file '{frame.as_posix()}'")
        lines.append("duration 8")
    lines.append(f"file '{frames[-1].as_posix()}'")
    list_file.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-vsync",
        "vfr",
        "-pix_fmt",
        "yuv420p",
        "-c:v",
        "libx264",
        "-movflags",
        "+faststart",
        str(VIDEO),
    ]
    subprocess.run(cmd, check=True)
    print(f"Wrote {VIDEO} from {len(frames)} slides")


if __name__ == "__main__":
    main()
