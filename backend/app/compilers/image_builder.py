"""
SovereignWorkbench — Visual Inspection Markup & Heatmap Compiler (app/compilers/image_builder.py)
Generates high-resolution annotated P&ID schematics and corrosion heatmaps (.png)
using Pillow. Highlights ultrasonic wall-thinning zones and safety clearances.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from app.schemas import ApprovalNotePayload, PipeInspectionData


def build_inspection_heatmap_image(
    payload: ApprovalNotePayload,
    output_path: Path
) -> Path:
    """
    Generate a 1600x900 annotated refinery P&ID inspection schematic and heatmap (.png).
    Highlights the degraded pipe segment with measured ultrasonic thickness callouts.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = payload.inspection_data

    width, height = 1600, 900
    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Slate dark #0F172A
    draw = ImageDraw.Draw(img)

    # 1. Subtle Engineering Grid
    for x in range(0, width, 50):
        draw.line([(x, 0), (x, height)], fill=(30, 41, 59), width=1)
    for y in range(0, height, 50):
        draw.line([(0, y), (width, y)], fill=(30, 41, 59), width=1)

    # 2. Header Banner
    draw.rectangle([(40, 30), (width - 40, 100)], fill=(30, 41, 59), outline=(6, 182, 212), width=2)
    draw.text((60, 42), "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)", fill=(6, 182, 212))
    draw.text((60, 68), f"AUTONOMOUS P&ID VISION AUDIT & CORROSION HEATMAP • {payload.unit_name}", fill=(248, 250, 252))
    draw.text((width - 320, 55), "AIR-GAP AQUANEX VERIFIED", fill=(16, 185, 129))

    # 3. Schematic Vessels
    # Crude Distillation Column (Left)
    col_x1, col_y1, col_x2, col_y2 = 120, 220, 260, 720
    draw.rectangle([(col_x1, col_y1), (col_x2, col_y2)], fill=(30, 41, 59), outline=(148, 163, 184), width=3)
    draw.ellipse([(col_x1, col_y1 - 30), (col_x2, col_y1 + 30)], outline=(148, 163, 184), fill=(30, 41, 59), width=3)
    draw.ellipse([(col_x1, col_y2 - 30), (col_x2, col_y2 + 30)], outline=(148, 163, 184), fill=(30, 41, 59), width=3)
    draw.text((col_x1 + 35, 450), "CDU-2 COLUMN", fill=(248, 250, 252))

    # Overhead Condenser (Right)
    cond_x1, cond_y1, cond_x2, cond_y2 = 1250, 260, 1480, 460
    draw.rectangle([(cond_x1, cond_y1), (cond_x2, cond_y2)], fill=(30, 41, 59), outline=(148, 163, 184), width=3)
    draw.text((cond_x1 + 30, 350), "E-201 CONDENSER", fill=(248, 250, 252))

    # 4. Connecting Piping Runs
    # Upstream pipe (Normal / Green)
    draw.line([(190, col_y1), (190, 180)], fill=(16, 185, 129), width=8)
    draw.line([(190, 180), (500, 180)], fill=(16, 185, 129), width=8)

    # Critical Thinning Pipe Segment (Line CDU-2-04-150-A1A) - Glowing RED / ORANGE
    # Glow effect
    for g in range(16, 6, -2):
        draw.line([(500, 180), (950, 180)], fill=(239, 68, 68), width=g)
    draw.line([(500, 180), (950, 180)], fill=(255, 255, 255), width=4)

    # Downstream pipe into condenser
    draw.line([(950, 180), (1365, 180)], fill=(16, 185, 129), width=8)
    draw.line([(1365, 180), (1365, cond_y1)], fill=(16, 185, 129), width=8)

    # 5. Inspection Callout Pin on Critical Segment
    pin_x = 725
    draw.circle((pin_x, 180), radius=14, fill=(239, 68, 68), outline=(255, 255, 255), width=3)
    draw.line([(pin_x, 180), (pin_x, 260)], fill=(239, 68, 68), width=3)
    draw.line([(pin_x, 260), (pin_x + 60, 310)], fill=(239, 68, 68), width=3)

    # Callout Info Card
    card_x1, card_y1, card_x2, card_y2 = pin_x - 100, 310, pin_x + 460, 560
    draw.rectangle([(card_x1, card_y1), (card_x2, card_y2)], fill=(15, 23, 42), outline=(239, 68, 68), width=3)

    draw.text((card_x1 + 20, card_y1 + 18), "🚨 CRITICAL CORROSION ALERT", fill=(239, 68, 68))
    draw.text((card_x1 + 20, card_y1 + 45), f"LINE TAG: {data.line_tag}", fill=(248, 250, 252))
    draw.text((card_x1 + 20, card_y1 + 75), f"Measured Thickness (UTG): {data.actual_thickness_mm:.2f} mm (Nominal: {data.nominal_thickness_mm:.2f} mm)", fill=(248, 250, 252))
    draw.text((card_x1 + 20, card_y1 + 105), f"Minimum Required (ASME B31.3): {data.minimum_required_thickness_mm:.2f} mm", fill=(248, 250, 252))
    draw.text((card_x1 + 20, card_y1 + 135), f"Corrosion Rate: {data.corrosion_rate_mm_year:.2f} mm/year", fill=(248, 250, 252))
    draw.text((card_x1 + 20, card_y1 + 165), f"REMAINING LIFE: {data.remaining_life_years:.2f} YEARS (< 5.0 YR THRESHOLD)", fill=(239, 68, 68))
    draw.text((card_x1 + 20, card_y1 + 195), f"ACTION: {data.mandatory_action}", fill=(6, 182, 212))

    # 6. Bottom Legend & Specs
    draw.rectangle([(40, height - 120), (width - 40, height - 40)], fill=(30, 41, 59), outline=(148, 163, 184), width=1)
    draw.text((60, height - 105), "LEGEND:", fill=(6, 182, 212))
    draw.line([(140, height - 95), (200, height - 95)], fill=(16, 185, 129), width=6)
    draw.text((215, height - 105), "Normal Remaining Life (> 5 Yrs)", fill=(248, 250, 252))

    draw.line([(480, height - 95), (540, height - 95)], fill=(239, 68, 68), width=6)
    draw.text((555, height - 105), "Critical Thinning / Replacement (< 5 Yrs)", fill=(239, 68, 68))

    draw.text((width - 500, height - 105), f"AUDITED BY: {data.inspector_name}", fill=(148, 163, 184))
    draw.text((width - 500, height - 75), f"REPORT DATE: {data.inspection_date}", fill=(148, 163, 184))

    img.save(str(output_path), format="PNG")
    return output_path
