import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import settings
from app.models.scan import Scan
from app.models.vulnerability import Severity, Vulnerability

_SEVERITY_COLOR = {
    Severity.CRITICAL: colors.HexColor("#7f1d1d"),
    Severity.HIGH: colors.HexColor("#b91c1c"),
    Severity.MEDIUM: colors.HexColor("#d97706"),
    Severity.LOW: colors.HexColor("#ca8a04"),
    Severity.INFO: colors.HexColor("#64748b"),
}


def generate_pdf_report(scan: Scan, vulnerabilities: list[Vulnerability], dest_path: str) -> None:
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(dest_path, pagesize=letter)

    elements = [
        Paragraph("Cloud Security Scanner — Scan Report", styles["Title"]),
        Spacer(1, 0.2 * inch),
        Paragraph(f"Target: {scan.target}", styles["Normal"]),
        Paragraph(f"Scan type: {scan.scan_type.value}", styles["Normal"]),
        Paragraph(f"Status: {scan.status.value}", styles["Normal"]),
        Paragraph(
            f"Security score: {scan.security_score if scan.security_score is not None else 'N/A'}/100",
            styles["Normal"],
        ),
        Spacer(1, 0.3 * inch),
        Paragraph(f"Findings ({len(vulnerabilities)})", styles["Heading2"]),
        Spacer(1, 0.1 * inch),
    ]

    rows = [["Severity", "Title", "Package", "CVE"]]
    for v in vulnerabilities:
        cve_cell = (
            Paragraph(f'<link href="{settings.CVE_LOOKUP_URL}{v.cve_id}">{v.cve_id}</link>', styles["Normal"])
            if v.cve_id
            else "-"
        )
        rows.append(
            [
                Paragraph(v.severity.value.upper(), styles["Normal"]),
                Paragraph(v.title, styles["Normal"]),
                Paragraph(v.package_name or "-", styles["Normal"]),
                cve_cell,
            ]
        )

    table = Table(rows, colWidths=[0.9 * inch, 2.8 * inch, 1.6 * inch, 1.4 * inch], repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]
    for i, v in enumerate(vulnerabilities, start=1):
        style_commands.append(("TEXTCOLOR", (0, i), (0, i), _SEVERITY_COLOR[v.severity]))
    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    doc.build(elements)
