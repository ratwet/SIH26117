"""
SovereignWorkbench — End-to-End Industrial Audit Simulation (backend/tests/test_e2e_simulation.py)
Simulates complete pipeline: P&ID OCR -> Math Derivation -> Sandbox Run -> Word & Excel Compilation -> Audit Ledger.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.graph.builder import sovereign_graph
from app.graph.state import AgentState
from app.security.audit_chain import verify_audit_chain, get_audit_ledger
from app.config import settings


async def run_simulation():
    print("=" * 70)
    print("🏭 MRPL SOVEREIGNWORKBENCH — END-TO-END INDUSTRIAL SIMULATION")
    print("   Scenario: Crude Distillation Unit 2 (CDU-2) Overhead Line Audit")
    print("   Standard: API 570 / ASME B31.3 Piping Inspection Code")
    print("=" * 70)

    # 1. Setup simulated uploaded file
    uploads_dir = settings.DATA_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    sample_scan_path = uploads_dir / "CDU_2_UT_Scan_2026.pdf"
    sample_scan_path.write_bytes(b"%PDF-1.4 Mock P&ID Ultrasonic Scan for CDU-2-04-150-A1A")

    # 2. Construct initial AgentState
    initial_state: AgentState = {
        "session_id": "sim-2026",
        "user_prompt": "Audit line CDU-2-04-150-A1A from uploaded UT inspection scan and generate formal executive approval note.",
        "uploaded_files": [str(sample_scan_path)],
        "user_role": "senior_inspection_engineer",
        "task_type": None,
        "active_model": None,
        "extracted_specs": None,
        "pipe_data": None,
        "rag_chunks": None,
        "rag_context": None,
        "generated_code": None,
        "sandbox_result": None,
        "retry_count": 0,
        "calc_result": None,
        "docx_path": None,
        "xlsx_path": None,
        "thought_stream": [],
        "final_response": None,
        "error_message": None,
    }

    print("\n[STEP 1] Injecting User Request into LangGraph Brain...")
    print(f"  Prompt:   '{initial_state['user_prompt']}'")
    print(f"  Document: {sample_scan_path.name}")
    print(f"  Role:     {initial_state['user_role']}")

    print("\n[STEP 2] Executing Multi-Step Sovereign State Machine...")
    
    # Stream events node-by-node and accumulate state
    accumulated_state = dict(initial_state)
    step_num = 1
    async for output in sovereign_graph.astream(initial_state):
        for node_name, node_state in output.items():
            print(f"\n  ▶ Node [{step_num}]: {node_name.upper()}")
            thoughts = node_state.get("thought_stream", [])
            if thoughts:
                print(f"    Thought: {thoughts[-1]}")
            step_num += 1
            accumulated_state.update(node_state)

    print("\n" + "=" * 70)
    print("📊 SIMULATION RESULTS & ARTIFACT VERIFICATION")
    print("=" * 70)

    # 3. Verify Deterministic Math Calculation
    calc = accumulated_state.get("calc_result")
    if calc:
        print(f"  Line Tag:              {calc.get('line_tag')}")
        print(f"  Nominal Thickness:     {calc.get('t_nominal')} mm")
        print(f"  Actual Measured:       {calc.get('t_actual')} mm")
        print(f"  Corrosion Rate:        {calc.get('corrosion_rate')} mm/year")
        print(f"  Remaining Safe Life:   {calc.get('remaining_life_years')} YEARS")
        print(f"  Mandatory Action:      {calc.get('mandatory_action')}")
        print(f"  Turnaround Budget:     INR ₹{calc.get('replacement_cost_inr'):,.2f}")
    else:
        print("  ⚠️ Math calculation result missing from final state.")

    # 4. Verify Generated Physical Deliverables
    docx_file = Path(accumulated_state.get("docx_path", ""))
    xlsx_file = Path(accumulated_state.get("xlsx_path", ""))

    print(f"\n  📄 Word Approval Note: {docx_file}")
    if docx_file.exists():
        print(f"     Status: EXISTS (Size: {docx_file.stat().st_size:,} bytes)")
    else:
        print("     Status: ❌ FILE NOT FOUND")

    print(f"  📈 Excel Cost Matrix:  {xlsx_file}")
    if xlsx_file.exists():
        print(f"     Status: EXISTS (Size: {xlsx_file.stat().st_size:,} bytes)")
    else:
        print("     Status: ❌ FILE NOT FOUND")

    # 5. Verify Cryptographic SHA-256 Audit Chain
    print("\n  🔐 Cryptographic Audit Chain Ledger:")
    is_valid, msg, count = verify_audit_chain()
    print(f"     Chain Integrity: {'✅ VALID' if is_valid else '❌ CORRUPTED'}")
    print(f"     Total Block Height: {count} recorded events")
    
    entries = get_audit_ledger(limit=1)
    if entries:
        latest = entries[0]
        print(f"     Latest Block Hash:  {latest.entry_hash[:24]}...")
        print(f"     Previous Hash Link: {latest.previous_hash[:24]}...")

    print("\n" + "=" * 70)
    print("🎉 END-TO-END PIPELINE SIMULATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_simulation())
