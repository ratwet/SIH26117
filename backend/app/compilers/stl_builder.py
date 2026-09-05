"""
SovereignWorkbench — 3D CAD Piping Spool STL Compiler (app/compilers/stl_builder.py)
Generates 3D printable and CAD-importable stereolithography meshes (.stl)
for ASME B31.3 replacement piping spools with raised-face weld-neck flanges.
Compatible with AutoCAD 3D, SolidWorks, FreeCAD, Blender, Navisworks, and Cura/Bambu slicers.
"""

from pathlib import Path
import math
from app.schemas import ApprovalNotePayload


def _write_cylinder_facets(f, r_out, r_in, z_start, z_end, segments=36):
    """Writes tubular cylinder facets (outer wall, inner bore, and end caps if needed)."""
    angles = [2 * math.pi * i / segments for i in range(segments + 1)]

    for i in range(segments):
        a1 = angles[i]
        a2 = angles[i + 1]

        # Outer wall vertices
        x1_o, y1_o = r_out * math.cos(a1), r_out * math.sin(a1)
        x2_o, y2_o = r_out * math.cos(a2), r_out * math.sin(a2)

        # Inner wall vertices
        x1_i, y1_i = r_in * math.cos(a1), r_in * math.sin(a1)
        x2_i, y2_i = r_in * math.cos(a2), r_in * math.sin(a2)

        # 1. Outer surface (2 triangles)
        # Normal pointing outward approximately
        n_x = math.cos((a1 + a2) / 2)
        n_y = math.sin((a1 + a2) / 2)
        f.write(f"  facet normal {n_x:.4f} {n_y:.4f} 0.0\n    outer loop\n")
        f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z_start:.3f}\n")
        f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} {z_start:.3f}\n")
        f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} {z_end:.3f}\n")
        f.write("    endloop\n  endfacet\n")

        f.write(f"  facet normal {n_x:.4f} {n_y:.4f} 0.0\n    outer loop\n")
        f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z_start:.3f}\n")
        f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} {z_end:.3f}\n")
        f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z_end:.3f}\n")
        f.write("    endloop\n  endfacet\n")

        # 2. Inner bore surface (2 triangles, normal inward)
        f.write(f"  facet normal {-n_x:.4f} {-n_y:.4f} 0.0\n    outer loop\n")
        f.write(f"      vertex {x1_i:.3f} {y1_i:.3f} {z_start:.3f}\n")
        f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} {z_end:.3f}\n")
        f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} {z_start:.3f}\n")
        f.write("    endloop\n  endfacet\n")

        f.write(f"  facet normal {-n_x:.4f} {-n_y:.4f} 0.0\n    outer loop\n")
        f.write(f"      vertex {x1_i:.3f} {y1_i:.3f} {z_start:.3f}\n")
        f.write(f"      vertex {x1_i:.3f} {y1_i:.3f} {z_end:.3f}\n")
        f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} {z_end:.3f}\n")
        f.write("    endloop\n  endfacet\n")


def compile_piping_spool_stl_3d(
    payload: ApprovalNotePayload,
    output_path: Path,
    segments: int = 48
) -> Path:
    """
    Generates a 3D ASCII STL mesh representing the ASME B31.3 replacement piping spool.
    Features:
    - 600 mm overall spool run length
    - Central Schedule 40 carbon steel pipe body (168.3 mm OD)
    - Hollow inner through-bore (161.9 mm ID)
    - Two Class 150 RF weld-neck flanges at ends (279.4 mm OD, 88.9 mm length)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = payload.inspection_data

    # Geometry parameters (mm)
    pipe_od = 168.3
    wall_thickness = data.nominal_thickness_mm  # 4.8 mm
    pipe_id = pipe_od - 2 * wall_thickness
    r_pipe_out = pipe_od / 2.0
    r_pipe_in = pipe_id / 2.0

    flange_od = 279.4
    r_flange_out = flange_od / 2.0
    flange_len = 88.9
    spool_len = 600.0

    z0 = 0.0
    z1 = flange_len
    z2 = spool_len - flange_len
    z3 = spool_len

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"solid ASME_B31_3_Piping_Spool_{data.line_tag}\n")

        # 1. Left Flange (z0 to z1)
        _write_cylinder_facets(f, r_flange_out, r_pipe_in, z0, z1, segments=segments)

        # 2. Main Pipe Body (z1 to z2)
        _write_cylinder_facets(f, r_pipe_out, r_pipe_in, z1, z2, segments=segments)

        # 3. Right Flange (z2 to z3)
        _write_cylinder_facets(f, r_flange_out, r_pipe_in, z2, z3, segments=segments)

        # 4. Flange End Faces (Flat annular caps at z=0 and z=spool_len)
        angles = [2 * math.pi * i / segments for i in range(segments + 1)]
        for i in range(segments):
            a1 = angles[i]
            a2 = angles[i + 1]

            # Face at z=0 (Normal: 0, 0, -1)
            x1_o, y1_o = r_flange_out * math.cos(a1), r_flange_out * math.sin(a1)
            x2_o, y2_o = r_flange_out * math.cos(a2), r_flange_out * math.sin(a2)
            x1_i, y1_i = r_pipe_in * math.cos(a1), r_pipe_in * math.sin(a1)
            x2_i, y2_i = r_pipe_in * math.cos(a2), r_pipe_in * math.sin(a2)

            f.write("  facet normal 0.0 0.0 -1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} 0.0\n")
            f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} 0.0\n")
            f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} 0.0\n")
            f.write("    endloop\n  endfacet\n")

            f.write("  facet normal 0.0 0.0 -1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} 0.0\n")
            f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} 0.0\n")
            f.write(f"      vertex {x1_i:.3f} {y1_i:.3f} 0.0\n")
            f.write("    endloop\n  endfacet\n")

            # Face at z=spool_len (Normal: 0, 0, 1)
            f.write("  facet normal 0.0 0.0 1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z3:.3f}\n")
            f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} {z3:.3f}\n")
            f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} {z3:.3f}\n")
            f.write("    endloop\n  endfacet\n")

            f.write("  facet normal 0.0 0.0 1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z3:.3f}\n")
            f.write(f"      vertex {x1_i:.3f} {y1_i:.3f} {z3:.3f}\n")
            f.write(f"      vertex {x2_i:.3f} {y2_i:.3f} {z3:.3f}\n")
            f.write("    endloop\n  endfacet\n")

            # Transition shoulder at z=z1 (between Flange OD and Pipe OD, Normal: 0, 0, 1)
            x1_po, y1_po = r_pipe_out * math.cos(a1), r_pipe_out * math.sin(a1)
            x2_po, y2_po = r_pipe_out * math.cos(a2), r_pipe_out * math.sin(a2)
            f.write("  facet normal 0.0 0.0 1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z1:.3f}\n")
            f.write(f"      vertex {x2_po:.3f} {y2_po:.3f} {z1:.3f}\n")
            f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} {z1:.3f}\n")
            f.write("    endloop\n  endfacet\n")

            f.write("  facet normal 0.0 0.0 1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z1:.3f}\n")
            f.write(f"      vertex {x1_po:.3f} {y1_po:.3f} {z1:.3f}\n")
            f.write(f"      vertex {x2_po:.3f} {y2_po:.3f} {z1:.3f}\n")
            f.write("    endloop\n  endfacet\n")

            # Transition shoulder at z=z2 (between Flange OD and Pipe OD, Normal: 0, 0, -1)
            f.write("  facet normal 0.0 0.0 -1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z2:.3f}\n")
            f.write(f"      vertex {x2_o:.3f} {y2_o:.3f} {z2:.3f}\n")
            f.write(f"      vertex {x2_po:.3f} {y2_po:.3f} {z2:.3f}\n")
            f.write("    endloop\n  endfacet\n")

            f.write("  facet normal 0.0 0.0 -1.0\n    outer loop\n")
            f.write(f"      vertex {x1_o:.3f} {y1_o:.3f} {z2:.3f}\n")
            f.write(f"      vertex {x2_po:.3f} {y2_po:.3f} {z2:.3f}\n")
            f.write(f"      vertex {x1_po:.3f} {y1_po:.3f} {z2:.3f}\n")
            f.write("    endloop\n  endfacet\n")

        f.write(f"endsolid ASME_B31_3_Piping_Spool_{data.line_tag}\n")

    return output_path
