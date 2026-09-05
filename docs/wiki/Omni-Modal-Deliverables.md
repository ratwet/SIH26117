# 📑 Omni-Modal Deliverables Suite

A primary limitation of traditional conversational chatbots in enterprise environments is the **"Copy-Paste Format Gap"**: chatbots output raw markdown text, forcing engineers to spend 2 to 3 hours manually transcribing numbers into corporate Word notes, Excel Capex sheets, AutoCAD drawings, and compliance dossiers.

Aquanex completely bridges this gap. When an engineering query or inspection drawing is processed, the platform autonomously compiles a **10-deliverable omni-modal publication suite** directly on-premise without requiring Microsoft Office, Adobe Acrobat, or Autodesk licenses.

---

## 📦 The 10 Statutory Deliverables

All deliverables are generated headlessly in [`backend/app/compilers/`](backend/app/compilers/) and deposited into `backend/data/deliverables/`:

| # | Filename | Format | Compiler Module | Purpose & Statutory Standard |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **`Inspection_Certificate.pdf`** | PDF | [`pdf_builder.py`](backend/app/compilers/pdf_builder.py) | Formal statutory certificate with digital signatures, QR verification, and OISD-STD-118/153 criteria. |
| **2** | **`Approval_Note.docx`** | DOCX | [`docx_builder.py`](backend/app/compilers/docx_builder.py) | Executive Board approval dossier styled with corporate typography and API 570 mandatory callout boxes. |
| **3** | **`Cost_Matrix.xlsx`** | XLSX | [`xlsx_builder.py`](backend/app/compilers/xlsx_builder.py) | Multi-tab Capex procurement budget with dynamic risk badges and formulaic replacement cost projections. |
| **4** | **`Executive_Pitch_Deck.pptx`**| PPTX | [`pptx_builder.py`](backend/app/compilers/pptx_builder.py) | High-contrast executive presentation deck summarizing integrity findings and Capex authorization. |
| **5** | **`Piping_Spool.dxf`** | DXF | [`cad_builder.py`](backend/app/compilers/cad_builder.py) | Production AutoCAD 2D drawing with dimensioned spool layout, flange specs, and ANSI layers. |
| **6** | **`Piping_Spool_3D.stl`** | STL | [`stl_builder.py`](backend/app/compilers/stl_builder.py) | 3D triangular mesh manifold model for rapid additive fabrication and 3D CAD inspection. |
| **7** | **`Inspection_Heatmap.png`** | PNG | [`image_builder.py`](backend/app/compilers/image_builder.py) | Visual P&ID schematic with color-coded corrosion severity gradients (Red / Amber / Green). |
| **8** | **`UT_Thickness_Survey.csv`** | CSV | [`csv_builder.py`](backend/app/compilers/csv_builder.py) | Tabular Condition Monitoring Location (CML) ultrasonic thickness survey log per OISD guidelines. |
| **9** | **`API570_Calculation.py`** | PY | Dynamic PAL Generator | Standalone, self-contained Python script for mathematically verifying all calculations independently. |
| **10**| **`Audit_Manifest.json`** | JSON | [`audit_chain.py`](backend/app/security/audit_chain.py) | Cryptographic manifest containing SHA-256 hashes, file sizes, and forward-linked ledger proofs. |

---

## 🔍 Detailed Specifications of Key Compilers

### 1. Statutory Inspection Certificate (`.pdf`)
* **Technology:** Built with `ReportLab` using programmatic canvas and flowable elements.
* **Features:**
  * High-resolution corporate header banner with official inspection title.
  * Verified QR Code containing document SHA-256 digest and certification ID for physical field validation.
  * Dual digital signature block for Plant Inspection Engineer and Lead Mechanical Integrity Officer.
  * Comprehensive table of ultrasonic Condition Monitoring Locations (CMLs).

### 2. Executive Board Approval Note (`.docx`)
* **Technology:** Built with `python-docx` adhering to institutional document guidelines.
* **Features:**
  * Standardized letterhead styling with corporate primary and secondary palettes.
  * **Dynamic Callout Alert Box:** If remaining life $RL \le 5.0\text{ years}$, the compiler automatically injects an urgent alert callout rendered in `#C00000` (Critical Alert Red) citing **API 570 Section 7.2** mandatory turnaround replacement.
  * Embedded Section 2 containing explicit step-by-step engineering formula derivations (ASME B31.3 $t_{\text{min}}$ and API 570 $RL$).

### 3. Capex Procurement Matrix (`.xlsx`)
* **Technology:** Built with `openpyxl` utilizing multi-tab workbook architecture.
* **Tabs Included:**
  1. `Executive Summary`: High-level asset identification, overall risk status, and total procurement budget.
  2. `Bill of Materials (BOM)`: Line-item breakdown of replacement spools, flanges, gaskets, weld consumables, and labor costs with dynamic Excel formulas (`SUM`, `PRODUCT`).
  3. `CML Inspection Log`: Complete dataset of historical ultrasonic wall-thickness readings.
* **Dynamic Risk Badging:** Utilizes openpyxl conditional formatting:
  * $RL \le 5.0\text{ yrs}$: `🔴 MANDATORY REPLACEMENT REQUIRED` (Bold white text on crimson fill).
  * $RL > 5.0\text{ yrs}$: `🟢 IN-SERVICE MONITORING ACCEPTABLE` (Dark green text on light green fill).

### 4. Production Piping Spool CAD (`.dxf`)
* **Technology:** Built with `ezdxf` generating clean, standard-compliant AutoCAD R2010 DXF files.
* **Layer Structuring:**
  * `CENTERLINE`: Dashed red centerlines for pipe routing.
  * `PIPE_WALLS`: Continuous white outlines representing outer pipe diameter.
  * `FLANGES`: Cyan geometries for weld-neck flanges.
  * `DIMENSIONS`: Green dimension arrows, extension lines, and numerical annotations.
  * `TITLE_BLOCK`: Border, revision block, and engineer approval stamp.

### 5. 3D Printable Manifold Mesh (`.stl`)
* **Technology:** Built with `numpy-stl` generating ASCII/binary stereolithography meshes.
* **Features:**
  * Parametric cylindrical coordinate transformations synthesizing faceted 3D cylindrical hulls, inner bores, and flange collars.
  * Ready for direct drag-and-drop viewing in Blender, FreeCAD, or 3D slicers for rapid turnaround prototyping.

---

## 🖥️ Zero-Dependency Native Architecture

All 10 compilers operate natively within standard Python virtual environments. They do **not** rely on COM-interop, wine, or third-party proprietary desktop applications:
* No Microsoft Office Word / Excel installation required.
* No Autodesk AutoCAD license required.
* Fully containerizable within minimal Linux containers (`ubuntu:24.04`, `fedora:40`, `alpine`).
