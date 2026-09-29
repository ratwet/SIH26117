#!/usr/bin/env python3
"""
generate_sih_presentation.py
Generates the official SIH 2026 Idea Submission PPTX from SIH2026-IDEA-Presentation-Format.original.pptx
Adheres strictly to SIH rules:
- Maximum 6 slides
- Pure Black (#000000) typography for 100% contrast, legibility and printing compliance
- Formatted in clean bullet points & structured key takeaways
- Includes all required prompt pointers
- Deletes Slide 7 (Instructions)
- Updates both SIH2026_Idea_Presentation_Filled.pptx and SIH2026-IDEA-Presentation-Format.pptx
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement

INPUT_PPTX = "/home/cyanide/SIH/SIH2026-IDEA-Presentation-Format.original.pptx"
if not os.path.exists(INPUT_PPTX):
    INPUT_PPTX = "/home/cyanide/SIH/SIH2026-IDEA-Presentation-Format.pptx"

OUTPUT_FILLED = "/home/cyanide/SIH/SIH2026_Idea_Presentation_Filled.pptx"
OUTPUT_MAIN = "/home/cyanide/SIH/SIH2026-IDEA-Presentation-Format.pptx"

PURE_BLACK = RGBColor(0, 0, 0)

def reset_paragraph_bullets(p, is_bullet=False):
    """Resets paragraph properties to eliminate rogue template bullet symbols and hanging indents."""
    pPr = p._p.get_or_add_pPr()
    for child in list(pPr):
        tag = child.tag.split('}')[-1]
        if tag.startswith('bu'):
            pPr.remove(child)
    
    if not is_bullet:
        pPr.set('marL', '0')
        pPr.set('indent', '0')
        buNone = OxmlElement('a:buNone')
        pPr.append(buNone)
    else:
        # Clean hanging indent for bullets (marL ~0.3in, indent ~-0.2in)
        pPr.set('marL', '280000')
        pPr.set('indent', '-200000')
        buNone = OxmlElement('a:buNone')
        pPr.append(buNone)

def style_para(p, text, size_pt=13, bold=False, level=0, space_after=4, is_bullet=False):
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.color.rgb = PURE_BLACK
    p.level = level
    p.space_after = Pt(space_after)
    reset_paragraph_bullets(p, is_bullet=is_bullet)
    for r in p.runs:
        r.font.name = "Arial"
        r.font.size = Pt(size_pt)
        r.font.bold = bold
        r.font.color.rgb = PURE_BLACK

def populate_slide(shape, sections):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.clear()
    
    first = True
    for sec_title, bullets in sections:
        if not first:
            p_sep = tf.add_paragraph()
            p_sep.space_after = Pt(4)
            reset_paragraph_bullets(p_sep, is_bullet=False)
        
        # Section Header (Bold Pure Black)
        p_hdr = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        style_para(p_hdr, f"▶ {sec_title}", size_pt=13, bold=True, level=0, space_after=3, is_bullet=False)
        
        # Bullet Points (Regular Pure Black with hanging indent)
        for bullet in bullets:
            p_b = tf.add_paragraph()
            style_para(p_b, f"•  {bullet}", size_pt=11.5, bold=False, level=0, space_after=3, is_bullet=True)

def enforce_pure_black_everywhere(prs):
    """Guarantees every text element across all shapes, tables, and slides is 100% pure black."""
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    p.font.color.rgb = PURE_BLACK
                    for r in p.runs:
                        r.font.color.rgb = PURE_BLACK
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            p.font.color.rgb = PURE_BLACK
                            for r in p.runs:
                                r.font.color.rgb = PURE_BLACK

def main():
    prs = Presentation(INPUT_PPTX)
    print(f"Loaded template from {INPUT_PPTX} with {len(prs.slides)} slides.")

    # -------------------------------------------------------------
    # SLIDE 1: TITLE PAGE
    # -------------------------------------------------------------
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.name == "Title 7":
            shape.top = Inches(0.2)
            shape.height = Inches(0.9)
            tf = shape.text_frame
            for p in tf.paragraphs:
                p.font.name = "Arial"
                p.font.bold = True
                p.font.color.rgb = PURE_BLACK
                reset_paragraph_bullets(p, is_bullet=False)
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.bold = True
                    r.font.color.rgb = PURE_BLACK

        elif shape.name == "Subtitle 3":
            shape.top = Inches(1.15)
            shape.height = Inches(1.1)
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            style_para(p, "AQUANEX", size_pt=24, bold=True, space_after=4, is_bullet=False)
            p2 = tf.add_paragraph()
            style_para(p2, "100% Air-Gapped Multimodal Engineering Intelligence for Refineries", size_pt=13, bold=False, is_bullet=False)
            
        elif shape.name == "TextBox 9":
            shape.top = Inches(2.45)
            shape.height = Inches(4.8)
            shape.width = Inches(6.8)
            tf = shape.text_frame
            tf.clear()
            lines = [
                ("Problem Statement ID:", "SIH26117"),
                ("Problem Statement Title:", "Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work"),
                ("Theme:", "Smart Automation"),
                ("PS Category:", "Software"),
                ("Organization:", "Mangalore Refinery and Petrochemicals Limited (MRPL / ONGC)"),
                ("Team ID:", "[Your Team ID]"),
                ("Team Name:", "[Your Team Name]"),
            ]
            first = True
            for label, val in lines:
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = f"{label} "
                p.font.name = "Arial"
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = PURE_BLACK
                p.space_after = Pt(4)
                reset_paragraph_bullets(p, is_bullet=False)
                
                # Style the prefix run
                if p.runs:
                    p.runs[0].font.name = "Arial"
                    p.runs[0].font.size = Pt(12)
                    p.runs[0].font.bold = True
                    p.runs[0].font.color.rgb = PURE_BLACK
                
                # Add and style the value run
                run = p.add_run()
                run.text = val
                run.font.name = "Arial"
                run.font.size = Pt(12)
                run.font.bold = False
                run.font.color.rgb = PURE_BLACK

    # -------------------------------------------------------------
    # SLIDE 2: PROPOSED SOLUTION
    # -------------------------------------------------------------
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.name == "Title 1":
            shape.text_frame.text = "PROPOSED SOLUTION: SOVEREIGNWORKBENCH"
            p = shape.text_frame.paragraphs[0]
            p.font.name = "Arial"
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = PURE_BLACK
            reset_paragraph_bullets(p, is_bullet=False)
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(24)
                r.font.bold = True
                r.font.color.rgb = PURE_BLACK
        elif "Oval" in shape.name:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    p.font.color.rgb = PURE_BLACK
                    for r in p.runs:
                        r.font.color.rgb = PURE_BLACK
        elif shape.name == "TextBox 8":
            shape.top = Inches(1.35)
            shape.height = Inches(5.3)
            shape.width = Inches(12.0)
            shape.left = Inches(0.67)
            populate_slide(shape, [
                ("Detailed Explanation of Proposed Solution", [
                    "100% self-hosted, air-gapped agentic AI workbench operating over an isolated 3-node physical LAN with zero cloud exfiltration.",
                    "Powered by open-weight foundation models (DeepSeek-R1 for reasoning, Qwen2.5-Coder for code synthesis, Qwen2-VL for P&ID blueprint OCR).",
                    "Automates refinery reliability workflows: technical P&ID drawing inspection, statutory life calculations (API 570 / ASME B31.3), and omni-modal deliverable generation."
                ]),
                ("How It Addresses the Problem", [
                    "Eliminates Cloud Leakage: Replaces prohibited public cloud LLMs (ChatGPT/Claude) with verified on-premise execution compliant with OISD & Official Secrets Act.",
                    "Eradicates Arithmetic Hallucination: Mathematical formulas are never computed via token generation; they are executed deterministically in an isolated Linux sandbox.",
                    "Self-Healing State Cycles: LangGraph cyclic state machine captures sandbox runtime exceptions, distills tracebacks, and self-corrects code automatically."
                ]),
                ("Innovation & Uniqueness", [
                    "Reactive Hardware/Kernel Air-Gap Kill Switch: Real-time socket & kernel route probe instantly freezes execution upon public Internet detection (403 Forbidden).",
                    "10-Deliverable Omni-Modal Suite: Autonomously compiles statutory PDFs, executive Word notes (.docx), live Excel cost matrices (.xlsx), AutoCAD drawings (.dxf), 3D STL meshes, and SHA-256 audit manifests."
                ])
            ])

    # -------------------------------------------------------------
    # SLIDE 3: TECHNICAL APPROACH
    # -------------------------------------------------------------
    s3 = prs.slides[2]
    for shape in s3.shapes:
        if shape.name == "Title 1":
            shape.text_frame.text = "TECHNICAL APPROACH & ARCHITECTURE"
            p = shape.text_frame.paragraphs[0]
            p.font.name = "Arial"
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = PURE_BLACK
            reset_paragraph_bullets(p, is_bullet=False)
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(24)
                r.font.bold = True
                r.font.color.rgb = PURE_BLACK
        elif "Oval" in shape.name:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    p.font.color.rgb = PURE_BLACK
                    for r in p.runs:
                        r.font.color.rgb = PURE_BLACK
        elif shape.name == "TextBox 8":
            shape.top = Inches(1.35)
            shape.height = Inches(5.3)
            shape.width = Inches(12.0)
            shape.left = Inches(0.67)
            populate_slide(shape, [
                ("Technologies & Frameworks", [
                    "Agentic Brain: LangGraph (Stateful cyclic graph with conditional routing) & FastAPI (Asynchronous SSE streaming text/event-stream).",
                    "AI Foundation Models: Multi-tier gateway supporting Ollama (3B/8B quantized on laptops) and vLLM cluster (70B/100B+ MoE on multi-GPU server).",
                    "Deterministic Sandbox: Linux Bubblewrap (bwrap) with read-only mounts (/usr, /lib, /bin), dedicated tmpfs, and RLIMIT_AS memory ceilings.",
                    "Sovereign RAG: FastEmbed (bge-small-en-v1.5) + ChromaDB vector database running 100% offline on CPU/GPU without cloud APIs.",
                    "Frontend & Desktop: Gemini/Claude-inspired clean UI, WebKit2 + GTK 3.0 native Linux desktop runner, Tauri v2 cross-platform integration."
                ]),
                ("Methodology & Implementation Process", [
                    "1. Ingestion & Intent Routing: Accepts P&ID blueprints, NDT logs, or SOP questions; routes between Vision, RAG, and Math nodes.",
                    "2. Multimodal OCR: Qwen2-VL extracts line tags (e.g. CDU-2-04-150-A1A), nominal thickness, and ultrasonic measured wall data.",
                    "3. RAG Grounding: Retrieves authoritative clauses from local repository of OISD-STD-118, API 570, and plant maintenance SOPs.",
                    "4. Sandboxed Code Execution: Reasoning model synthesizes Python script; executed in bwrap sandbox with autonomous 3-cycle error distillation.",
                    "5. Omni-Modal Compilation: Compiles 10 publication-ready files and logs tamper-evident SHA-256 hashes to immutable SQLite audit ledger."
                ])
            ])

    # -------------------------------------------------------------
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # -------------------------------------------------------------
    s4 = prs.slides[3]
    for shape in s4.shapes:
        if shape.name == "Title 1":
            shape.text_frame.text = "FEASIBILITY AND VIABILITY"
            p = shape.text_frame.paragraphs[0]
            p.font.name = "Arial"
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = PURE_BLACK
            reset_paragraph_bullets(p, is_bullet=False)
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(24)
                r.font.bold = True
                r.font.color.rgb = PURE_BLACK
        elif "Oval" in shape.name:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    p.font.color.rgb = PURE_BLACK
                    for r in p.runs:
                        r.font.color.rgb = PURE_BLACK
        elif shape.name == "TextBox 8":
            shape.top = Inches(1.35)
            shape.height = Inches(5.3)
            shape.width = Inches(12.0)
            shape.left = Inches(0.67)
            populate_slide(shape, [
                ("Operational Feasibility & Production Scalability", [
                    "Hardware Agnostic: Runs comfortably on a standard single engineering laptop (3B/8B models) and seamlessly scales to datacenter clusters (100B+ vLLM) with zero code modifications.",
                    "Fully Working Prototype: Proven codebase with 40/40 passing unit/integration tests, sub-second token latency, and live GTK desktop packaging.",
                    "Zero Recurring API Cost: Built exclusively on open-weight models and open-source infrastructure (MIT / Apache 2.0 licenses)."
                ]),
                ("Potential Challenges & Technical Risks", [
                    "Risk 1 (Data Exfiltration): Accidental connection of plant floor laptops to public Wi-Fi or mobile hotspots.",
                    "Risk 2 (Safety Hallucination): LLMs incorrectly predicting Remaining Safe Life below mandatory 5-year shutdown thresholds.",
                    "Risk 3 (Hardware Scarcity): High VRAM requirements for enterprise-scale 70B/100B+ reasoning models."
                ]),
                ("Mitigation Strategies", [
                    "Strategy 1 (Hardware/Kernel Kill Switch): Active socket probe monitors /proc/net/route; freezes memory and locks UI instantly on WAN egress.",
                    "Strategy 2 (Deterministic Muscle): Math calculations are 100% offloaded to Python scripts in bwrap sandbox; token generation never predicts arithmetic.",
                    "Strategy 3 (Distributed LAN Topology): Physical 3-node architecture offloads inference to an on-premise GPU workstation via isolated LAN."
                ])
            ])

    # -------------------------------------------------------------
    # SLIDE 5: IMPACT AND BENEFITS
    # -------------------------------------------------------------
    s5 = prs.slides[4]
    for shape in s5.shapes:
        if shape.name == "Title 1":
            shape.text_frame.text = "IMPACT AND BENEFITS"
            p = shape.text_frame.paragraphs[0]
            p.font.name = "Arial"
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = PURE_BLACK
            reset_paragraph_bullets(p, is_bullet=False)
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(24)
                r.font.bold = True
                r.font.color.rgb = PURE_BLACK
        elif "Oval" in shape.name:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    p.font.color.rgb = PURE_BLACK
                    for r in p.runs:
                        r.font.color.rgb = PURE_BLACK
        elif shape.name == "TextBox 8":
            shape.top = Inches(1.35)
            shape.height = Inches(5.3)
            shape.width = Inches(12.0)
            shape.left = Inches(0.67)
            populate_slide(shape, [
                ("Impact on Target Audience (MRPL, Refineries, PSUs & Defense)", [
                    "90% Turnaround Time Reduction: Compresses statutory piping inspection analysis from 3 hours to under 45 seconds per pipeline circuit.",
                    "Absolute Regulatory Compliance: 100% air-gapped sovereignty guarantees zero violations of CERT-In, OISD, and MoPNG cybersecurity directives.",
                    "Enhanced Plant Safety: Eliminates human calculation errors and enforces mandatory shutdown flags when Remaining Life is < 5.0 years."
                ]),
                ("Comprehensive Multi-Dimensional Benefits", [
                    "Economic: Estimated savings of ₹1.2+ Crores annually per refinery unit by avoiding unplanned plant shutdowns and expensive proprietary software licenses.",
                    "Environmental: Prevents hazardous hydrocarbon vapor leaks, pipeline ruptures, and flaring through verified predictive corrosion tracking.",
                    "Social & Operational: Standardizes organizational knowledge; junior engineers can reliably generate executive dossiers identical to senior inspection specialists."
                ])
            ])

    # -------------------------------------------------------------
    # SLIDE 6: RESEARCH AND REFERENCES
    # -------------------------------------------------------------
    s6 = prs.slides[5]
    for shape in s6.shapes:
        if shape.name == "Title 1":
            shape.text_frame.text = "RESEARCH AND REFERENCES"
            p = shape.text_frame.paragraphs[0]
            p.font.name = "Arial"
            p.font.size = Pt(24)
            p.font.bold = True
            p.font.color.rgb = PURE_BLACK
            reset_paragraph_bullets(p, is_bullet=False)
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(24)
                r.font.bold = True
                r.font.color.rgb = PURE_BLACK
        elif "Oval" in shape.name:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    p.font.color.rgb = PURE_BLACK
                    for r in p.runs:
                        r.font.color.rgb = PURE_BLACK
        elif shape.name == "TextBox 8":
            shape.top = Inches(1.35)
            shape.height = Inches(5.3)
            shape.width = Inches(12.0)
            shape.left = Inches(0.67)
            populate_slide(shape, [
                ("Statutory Engineering Codes & Standards", [
                    "API 570 (4th Ed.): Piping Inspection Code: In-service Inspection, Rating, Repair, and Alteration of Piping Systems (Sections 7.1.1 Remaining Life & 7.1.2 Corrosion Rate).",
                    "ASME B31.3 (2022): Process Piping Code (Paragraph 304.1.2 Straight Pipe Under Internal Pressure — Design Minimum Thickness tm).",
                    "OISD-STD-118: Oil Industry Safety Directorate — Layouts, Inspection Protocols & Maintenance Safety in Petroleum Refineries."
                ]),
                ("Technical References & Scientific Foundations", [
                    "LangGraph & LangChain: Stateful Multi-Actor Agentic Orchestration with Cyclic Directed Graph Workflows (Harrison Chase et al., 2024).",
                    "DeepSeek-R1: Incentivizing Reasoning Capability in Large Language Models via Reinforcement Learning (DeepSeek-AI, 2025).",
                    "Linux Bubblewrap (bwrap): Unprivileged Sandboxing and Container Namespace Isolation (GNOME Foundation / Project Atomic).",
                    "ChromaDB & FastEmbed: Quantized Dense Vector Embeddings (BAAI/bge-small-en-v1.5) for Low-Latency Sovereign RAG.",
                    "FastAPI & WebKitGTK: Asynchronous Event-Stream Architecture & Linux Native GUI Client Implementation."
                ])
            ])

    # -------------------------------------------------------------
    # SLIDE 7: INSTRUCTION SLIDE -> DELETE
    # -------------------------------------------------------------
    if len(prs.slides) > 6:
        rId = prs.slides._sldIdLst[6].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[6]
        print("Deleted Slide 7 (Instructions) to satisfy the strict 6-slide limit.")

    # Global enforcement pass
    enforce_pure_black_everywhere(prs)

    # Save to both destinations
    prs.save(OUTPUT_FILLED)
    prs.save(OUTPUT_MAIN)
    print(f"✅ Successfully generated filled presentation with 100% PURE BLACK text:")
    print(f"   -> {OUTPUT_FILLED}")
    print(f"   -> {OUTPUT_MAIN}")

if __name__ == "__main__":
    main()
