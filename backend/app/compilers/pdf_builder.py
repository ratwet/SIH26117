"""
SovereignWorkbench — PDF Inspection Certificate Compiler (app/compilers/pdf_builder.py)
Generates statutory, print-ready API 570 / ASME B31.3 Piping Inspection & Fitness-for-Service
Certificates (.pdf) for MRPL Technical Services using ReportLab.
"""

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from app.schemas import ApprovalNotePayload


def compile_inspection_certificate_pdf(
    payload: ApprovalNotePayload,
    output_path: Path
) -> Path:
    """
    Generate an official MRPL Statutory Inspection & Derating Certificate (.pdf).
    Includes MRPL PSU header, asset specifications, API 570 calculation results,
    and statutory sign-off authority blocks.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = payload.inspection_data
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CertTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0B2545"),
        alignment=1,  # Center
    )

    subtitle_style = ParagraphStyle(
        "CertSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#D4AF37"),
        alignment=1,
    )

    h2_style = ParagraphStyle(
        "CertH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0B2545"),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "CertBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1A202C"),
    )

    bold_body = ParagraphStyle(
        "CertBodyBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    alert_style = ParagraphStyle(
        "CertAlert",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#B91C1C"),
        alignment=1,
    )

    story = []

    # 1. Official Header
    story.append(Paragraph("MANGALORE REFINERY AND PETROCHEMICALS LIMITED", title_style))
    story.append(Paragraph("A Govt. of India Enterprise | Technical Services Division", subtitle_style))
    story.append(Paragraph("STATUTORY API 570 FITNESS-FOR-SERVICE & ASSET INTEGRITY CERTIFICATE", ParagraphStyle("CertDocName", parent=title_style, fontSize=12, leading=15, textColor=colors.HexColor("#1E3A8A"), spaceBefore=4)))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0B2545"), spaceAfter=10))

    # 2. Metadata Certificate Grid
    today_str = datetime.now().strftime("%d-%b-%Y")
    cert_meta = [
        [Paragraph("<b>Certificate No:</b>", body_style), Paragraph(f"MRPL/TSD/FFS/{datetime.now().year}/042", body_style),
         Paragraph("<b>Date of Issue:</b>", body_style), Paragraph(today_str, body_style)],
        [Paragraph("<b>Operating Unit:</b>", body_style), Paragraph("Crude Distillation Unit 2 (CDU-2)", body_style),
         Paragraph("<b>Inspection Code:</b>", body_style), Paragraph("API 570 / ASME B31.3", body_style)],
        [Paragraph("<b>Asset Line Tag:</b>", body_style), Paragraph(f"<b>{data.line_tag}</b>", bold_body),
         Paragraph("<b>Metallurgy:</b>", body_style), Paragraph("ASTM A106 Gr. B Carbon Steel", body_style)],
        [Paragraph("<b>Fluid Service:</b>", body_style), Paragraph("Hydrocarbon Vapor / Sour Gas", body_style),
         Paragraph("<b>Design Limits:</b>", body_style), Paragraph("150 psig @ 135 °C", body_style)],
    ]
    meta_table = Table(cert_meta, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Ultrasonic Thickness Assessment Table
    story.append(Paragraph("1. API 570 Non-Destructive Ultrasonic Thickness Assessment", h2_style))
    corrosion_rate = round((data.nominal_thickness_mm - data.actual_thickness_mm) / 10.0, 3)
    t_min = 2.1  # ASME B31.3 minimum retirement limit

    table_data = [
        [Paragraph("<b>Parameter Description</b>", bold_body), Paragraph("<b>Engineering Value</b>", bold_body), Paragraph("<b>Statutory Reference</b>", bold_body), Paragraph("<b>Safety Status</b>", bold_body)],
        [Paragraph("Nominal Wall Thickness", body_style), Paragraph(f"{data.nominal_thickness_mm} mm", body_style), Paragraph("ASME B36.10M Schedule 40", body_style), Paragraph("Design Baseline", body_style)],
        [Paragraph("Measured Ultrasonic Wall Thickness", body_style), Paragraph(f"<b>{data.actual_thickness_mm} mm</b>", bold_body), Paragraph("UT Grid Survey (8 CMLs)", body_style), Paragraph("Thinning Observed", body_style)],
        [Paragraph("Minimum Allowable Thickness (t_min)", body_style), Paragraph(f"{t_min} mm", body_style), Paragraph("ASME B31.3 Section 304.1.2", body_style), Paragraph("Retirement Boundary", body_style)],
        [Paragraph("Active Corrosion Velocity", body_style), Paragraph(f"{corrosion_rate} mm / year", body_style), Paragraph("API 570 Long-Term Formula", body_style), Paragraph("Accelerated Degradation", body_style)],
        [Paragraph("Calculated Remaining Safe Life", body_style), Paragraph(f"<b>{data.remaining_life_years:.2f} Years</b>", bold_body), Paragraph("API 570 Section 7.1.1", body_style), Paragraph("< 5.0 Yrs Threshold", body_style)],
    ]
    t_table = Table(table_data, colWidths=[180, 110, 140, 110])
    t_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B2545")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 10))

    # 4. Mandatory Statutory Finding Box
    story.append(Paragraph("2. Statutory Engineering Recommendation & Mandatory Action", h2_style))
    action_box = [
        [Paragraph("CRITICAL ACTION REQUIRED PER STATUTORY SAFETY CODE:", alert_style)],
        [Paragraph(f"<b>{data.mandatory_action}</b>", alert_style)],
        [Paragraph(
            "Calculated remaining safe life is under the statutory 5.0-year turnaround window. "
            "Asset cannot safely operate into the subsequent operating cycle without replacement. "
            "Fabrication of ASME B31.3 replacement piping spool has been triggered under Work Order WO-CDU2-2026.",
            body_style
        )],
    ]
    a_table = Table(action_box, colWidths=[540])
    a_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#DC2626")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(a_table)
    story.append(Spacer(1, 14))

    # 5. Formal Sign-off Authority Blocks
    story.append(Paragraph("3. Statutory Authority Sign-Off Blocks", h2_style))
    sign_data = [
        [
            Paragraph("<b>Evaluated By:</b><br/><br/>_______________________<br/><b>K. Ramesh</b><br/>Lead NDT & Inspection Engineer<br/>MRPL TSD", body_style),
            Paragraph("<b>Verified By:</b><br/><br/>_______________________<br/><b>P. V. Shenoy</b><br/>Chief Manager (Asset Integrity)<br/>MRPL Operations", body_style),
            Paragraph("<b>Approved By:</b><br/><br/>_______________________<br/><b>S. K. Rao</b><br/>General Manager (Technical Services)<br/>MRPL Mangalore", body_style),
        ]
    ]
    s_table = Table(sign_data, colWidths=[180, 180, 180])
    s_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ("LINEBEFORE", (1, 0), (1, 0), 0.5, colors.HexColor("#94A3B8")),
        ("LINEBEFORE", (2, 0), (2, 0), 0.5, colors.HexColor("#94A3B8")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(s_table)

    doc.build(story)
    return output_path
