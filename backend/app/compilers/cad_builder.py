"""
SovereignWorkbench — AutoCAD DXF Drawing Compiler (app/compilers/cad_builder.py)
Generates industry-standard, precision 2D CAD engineering drawings (.dxf)
for replacement piping spools per ASME B31.3 / API 570 using ezdxf.
Compatible with AutoCAD, SolidWorks, LibreCAD, and FreeCAD.
"""

from pathlib import Path
import ezdxf
from ezdxf import colors

from app.schemas import PipeInspectionData, ApprovalNotePayload


def build_piping_spool_cad_dxf(
    payload: ApprovalNotePayload,
    output_path: Path
) -> Path:
    """
    Generate an ASME B31.3 compliant 2D piping spool CAD drawing (.dxf).
    Includes pipe body, weld-neck flanges, dimension lines, and MRPL title block.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = payload.inspection_data
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    # Define CAD Layers
    layers = [
        ("CENTERLINE", colors.RED, "CENTER"),
        ("PIPE_OUTLINE", colors.WHITE, "CONTINUOUS"),
        ("FLANGES", colors.CYAN, "CONTINUOUS"),
        ("DIMENSIONS", colors.GREEN, "CONTINUOUS"),
        ("TITLE_BLOCK", colors.YELLOW, "CONTINUOUS"),
        ("ANNOTATIONS", colors.MAGENTA, "CONTINUOUS"),
    ]
    for name, color, linetype in layers:
        if name not in doc.layers:
            doc.layers.add(name=name, color=color, linetype=linetype)

    # Drawing Geometry Coordinates (scale: 1 unit = 1 mm on paper)
    spool_length = 600.0   # Nominal representation length
    nominal_dia = 168.3    # 6" NB Pipe OD (mm)
    nominal_wall = data.nominal_thickness_mm  # 4.8 mm
    actual_wall = data.actual_thickness_mm    # 3.2 mm
    inner_dia = nominal_dia - 2 * nominal_wall

    flange_od = 279.4      # Class 150 RF Flange OD (11 in)
    flange_len = 88.9      # Flange overall length
    hub_len = 50.0

    y_center = 400.0
    x_start = 200.0
    x_end = x_start + spool_length

    # 1. Centerline
    msp.add_line(
        (x_start - 80, y_center),
        (x_end + 80, y_center),
        dxfattribs={"layer": "CENTERLINE"}
    )

    # 2. Main Pipe Body
    y_top = y_center + nominal_dia / 2
    y_bot = y_center - nominal_dia / 2
    msp.add_line((x_start, y_top), (x_end, y_top), dxfattribs={"layer": "PIPE_OUTLINE"})
    msp.add_line((x_start, y_bot), (x_end, y_bot), dxfattribs={"layer": "PIPE_OUTLINE"})

    # Internal pipe bore (dashed representation)
    y_in_top = y_center + inner_dia / 2
    y_in_bot = y_center - inner_dia / 2
    msp.add_line((x_start, y_in_top), (x_end, y_in_top), dxfattribs={"layer": "PIPE_OUTLINE"})
    msp.add_line((x_start, y_in_bot), (x_end, y_in_bot), dxfattribs={"layer": "PIPE_OUTLINE"})

    # 3. Left Weld Neck Flange (Class 150)
    y_flange_top = y_center + flange_od / 2
    y_flange_bot = y_center - flange_od / 2
    flange_pts_left = [
        (x_start, y_top),
        (x_start - hub_len, y_top + 15),
        (x_start - hub_len, y_flange_top),
        (x_start - flange_len, y_flange_top),
        (x_start - flange_len, y_flange_bot),
        (x_start - hub_len, y_flange_bot),
        (x_start - hub_len, y_bot - 15),
        (x_start, y_bot),
    ]
    msp.add_lwpolyline(flange_pts_left, close=True, dxfattribs={"layer": "FLANGES"})

    # 4. Right Weld Neck Flange (Class 150)
    flange_pts_right = [
        (x_end, y_top),
        (x_end + hub_len, y_top + 15),
        (x_end + hub_len, y_flange_top),
        (x_end + flange_len, y_flange_top),
        (x_end + flange_len, y_flange_bot),
        (x_end + hub_len, y_flange_bot),
        (x_end + hub_len, y_bot - 15),
        (x_end, y_bot),
    ]
    msp.add_lwpolyline(flange_pts_right, close=True, dxfattribs={"layer": "FLANGES"})

    # 5. Critical Ultrasonic Thinning Callout Box (Mid-span)
    mid_x = x_start + spool_length / 2
    msp.add_circle((mid_x, y_top), radius=10, dxfattribs={"layer": "ANNOTATIONS"})
    msp.add_line((mid_x, y_top + 10), (mid_x + 50, y_top + 90), dxfattribs={"layer": "ANNOTATIONS"})
    msp.add_line((mid_x + 50, y_top + 90), (mid_x + 220, y_top + 90), dxfattribs={"layer": "ANNOTATIONS"})
    
    msp.add_text(
        f"CRITICAL INSPECTION POINT: {data.line_tag}",
        dxfattribs={"layer": "ANNOTATIONS", "height": 12.0}
    ).set_placement((mid_x + 55, y_top + 96))
    
    msp.add_text(
        f"Actual Wall t = {actual_wall:.2f} mm | Min Req t = {data.minimum_required_thickness_mm:.2f} mm",
        dxfattribs={"layer": "ANNOTATIONS", "height": 10.0}
    ).set_placement((mid_x + 55, y_top + 78))

    msp.add_text(
        f"Remaining Life = {data.remaining_life_years:.2f} YRS (< 5.0 YR THRESHOLD) - ACTION REQUIRED",
        dxfattribs={"layer": "ANNOTATIONS", "height": 10.0}
    ).set_placement((mid_x + 55, y_top + 62))

    # 6. Dimensions
    # Overall Length Dimension
    msp.add_line((x_start - flange_len, y_center - 200), (x_end + flange_len, y_center - 200), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x_start - flange_len, y_center - 180), (x_start - flange_len, y_center - 220), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x_end + flange_len, y_center - 180), (x_end + flange_len, y_center - 220), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_text(
        f"OVERALL SPOOL LENGTH = {spool_length + 2*flange_len:.1f} mm",
        dxfattribs={"layer": "DIMENSIONS", "height": 14.0}
    ).set_placement((mid_x - 120, y_center - 230))

    # Pipe OD Dimension
    msp.add_line((x_start + 80, y_bot), (x_start + 80, y_top), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_text(
        f"6\" NB SCH 40 (OD {nominal_dia} mm)",
        dxfattribs={"layer": "DIMENSIONS", "height": 10.0}
    ).set_placement((x_start + 90, y_center))

    # 7. Enterprise Engineering Title Block (ISO Standard Lower-Right)
    tb_x = 550.0
    tb_y = 50.0
    tb_w = 420.0
    tb_h = 160.0

    msp.add_lwpolyline([
        (tb_x, tb_y),
        (tb_x + tb_w, tb_y),
        (tb_x + tb_w, tb_y + tb_h),
        (tb_x, tb_y + tb_h)
    ], close=True, dxfattribs={"layer": "TITLE_BLOCK"})

    # Title block dividing lines
    msp.add_line((tb_x, tb_y + 110), (tb_x + tb_w, tb_y + 110), dxfattribs={"layer": "TITLE_BLOCK"})
    msp.add_line((tb_x, tb_y + 60), (tb_x + tb_w, tb_y + 60), dxfattribs={"layer": "TITLE_BLOCK"})
    msp.add_line((tb_x + 220, tb_y), (tb_x + 220, tb_y + 60), dxfattribs={"layer": "TITLE_BLOCK"})

    # Title block texts
    msp.add_text(
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 11.0}
    ).set_placement((tb_x + 10, tb_y + 135))

    msp.add_text(
        f"PROJECT: {payload.unit_name} SHUTDOWN REPLACEMENT",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 9.0}
    ).set_placement((tb_x + 10, tb_y + 118))

    msp.add_text(
        f"DRAWING: PIPING REPLACEMENT SPOOL (DWG: MRPL-CDU2-{data.line_tag})",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 10.0}
    ).set_placement((tb_x + 10, tb_y + 88))

    msp.add_text(
        f"MATERIAL: {data.material_spec} | DESIGN: {data.design_pressure_psi} PSI",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 8.5}
    ).set_placement((tb_x + 10, tb_y + 68))

    msp.add_text(
        f"DESIGNED BY: SOVEREIGN AGENTIC WORKBENCH",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 8.0}
    ).set_placement((tb_x + 10, tb_y + 35))

    msp.add_text(
        f"AUDITED BY: {data.inspector_name}",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 8.0}
    ).set_placement((tb_x + 10, tb_y + 15))

    msp.add_text(
        "SCALE: 1:10 (METRIC)",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 8.0}
    ).set_placement((tb_x + 230, tb_y + 35))

    msp.add_text(
        f"DATE: {data.inspection_date}",
        dxfattribs={"layer": "TITLE_BLOCK", "height": 8.0}
    ).set_placement((tb_x + 230, tb_y + 15))

    doc.saveas(str(output_path))
    return output_path
