import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.classifier import classify
from agents.evidence_extractor import extract_evidence
from agents.department_router import route_department
from agents.response_drafter import draft_response
from agents.task_generator import generate_tasks


# Pipeline ka State — har agent ka output yahan store hoga
class CivicState(TypedDict):
    complaint_text: str
    complaint_id: Optional[int]
    classifier_result: Optional[dict]
    evidence: Optional[dict]
    dept_result: Optional[dict]
    draft_result: Optional[dict]
    tasks: Optional[list]
    escalate_immediately: Optional[bool]
    error: Optional[str]


# ── Node 1: Classifier ──────────────────────────────
def node_classifier(state: CivicState) -> CivicState:
    try:
        complaint_id, result = classify(state["complaint_text"])
        return {
            **state,
            "complaint_id": complaint_id,
            "classifier_result": result,
            "error": None
        }
    except Exception as e:
        return {**state, "error": f"Classifier failed: {str(e)}"}


# ── Node 2: Evidence Extractor ──────────────────────
def node_evidence(state: CivicState) -> CivicState:
    try:
        result = extract_evidence(
            state["complaint_text"],
            state["complaint_id"]
        )
        return {**state, "evidence": result}
    except Exception as e:
        return {**state, "error": f"Evidence extractor failed: {str(e)}"}


# ── Node 3: Department Router ───────────────────────
def node_router(state: CivicState) -> CivicState:
    try:
        result = route_department(
            complaint_id=state["complaint_id"],
            issue_type=state["classifier_result"]["issue_type"],
            urgency=state["classifier_result"]["urgency"],
            evidence=state["evidence"]
        )
        return {
            **state,
            "dept_result": result,
            "escalate_immediately": result.get("escalate_immediately", False)
        }
    except Exception as e:
        return {**state, "error": f"Router failed: {str(e)}"}


# ── Node 4: Response Drafter ────────────────────────
def node_drafter(state: CivicState) -> CivicState:
    try:
        result = draft_response(
            complaint_id=state["complaint_id"],
            complaint_text=state["complaint_text"],
            classifier_result=state["classifier_result"],
            evidence=state["evidence"],
            dept_result=state["dept_result"]
        )
        return {**state, "draft_result": result}
    except Exception as e:
        return {**state, "error": f"Drafter failed: {str(e)}"}


# ── Node 5: Task Generator ──────────────────────────
def node_tasks(state: CivicState) -> CivicState:
    try:
        tasks = generate_tasks(
            complaint_id=state["complaint_id"],
            classifier_result=state["classifier_result"],
            dept_result=state["dept_result"],
            evidence=state["evidence"]
        )
        return {**state, "tasks": tasks}
    except Exception as e:
        return {**state, "error": f"Task generator failed: {str(e)}"}


# ── Escalation check ────────────────────────────────
def should_escalate(state: CivicState) -> str:
    if state.get("error"):
        return "end"
    if state.get("escalate_immediately"):
        return "escalate"
    return "normal"


# ── Escalation Node ─────────────────────────────────
def node_escalate(state: CivicState) -> CivicState:
    print("\n🚨 ESCALATION TRIGGERED!")
    print(f"   Urgency {state['classifier_result']['urgency']}/5 — Immediate action required")
    print(f"   Contact: {state['dept_result'].get('contact', 'N/A')}")
    return state


# ── Build Graph ─────────────────────────────────────
def build_pipeline():
    graph = StateGraph(CivicState)

    # Nodes add karo
    graph.add_node("classifier", node_classifier)
    graph.add_node("evidence", node_evidence)
    graph.add_node("router", node_router)
    graph.add_node("escalate", node_escalate)
    graph.add_node("drafter", node_drafter)
    graph.add_node("tasks", node_tasks)

    # Edges — flow define karo
    graph.set_entry_point("classifier")
    graph.add_edge("classifier", "evidence")
    graph.add_edge("evidence", "router")

    # Router ke baad — escalate ya normal
    graph.add_conditional_edges(
        "router",
        should_escalate,
        {
            "escalate": "escalate",
            "normal": "drafter",
            "end": END
        }
    )

    graph.add_edge("escalate", "drafter")
    graph.add_edge("drafter", "tasks")
    graph.add_edge("tasks", END)

    return graph.compile()


# ── Run Pipeline ────────────────────────────────────
def run_pipeline(complaint_text: str):
    print("\n" + "=" * 55)
    print("🚀 CIVIC COPILOT PIPELINE STARTING")
    print("=" * 55)
    print(f"📝 Complaint: {complaint_text[:80]}...")
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")

    pipeline = build_pipeline()

    initial_state = CivicState(
        complaint_text=complaint_text,
        complaint_id=None,
        classifier_result=None,
        evidence=None,
        dept_result=None,
        draft_result=None,
        tasks=None,
        escalate_immediately=False,
        error=None
    )

    final_state = pipeline.invoke(initial_state)

    print("\n" + "=" * 55)
    print("✅ PIPELINE COMPLETE")
    print("=" * 55)

    if final_state.get("error"):
        print(f"❌ Error: {final_state['error']}")
        return None

    # Summary print karo
    clf = final_state["classifier_result"]
    dept = final_state["dept_result"]
    draft = final_state["draft_result"]
    tasks = final_state["tasks"]

    print(f"\n📊 SUMMARY:")
    print(f"   Issue Type  : {clf['issue_type'].upper()}")
    print(f"   Urgency     : {clf['urgency']}/5")
    print(f"   Language    : {clf['language']}")
    print(f"   Department  : {dept['department']}")
    print(f"   Officer     : {dept['officer']}")
    print(f"   SLA         : {dept['sla_days']} days")
    print(f"   Letter Type : {draft['letter_type']}")
    print(f"   Tasks       : {len(tasks)} action items")
    print(f"   Escalate    : {'🚨 YES' if final_state['escalate_immediately'] else '✅ NO'}")

    print(f"\n📄 LETTER PREVIEW (first 300 chars):")
    print("-" * 55)
    print(draft["letter_text"][:300] + "...")
    print("-" * 55)

    print(f"\n📋 ACTION PLAN:")
    for task in tasks:
        icon = "🚨" if task["priority"] == "CRITICAL" else "🔴" if task["priority"] == "HIGH" else "🟡"
        print(f"   {icon} {task['due_date']} — {task['action'][:55]}")

    print(f"\n⏰ Completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 55)

    return final_state


if __name__ == "__main__":
    print("🏛️  CIVIC COPILOT — Policy to Action")
    print("Apni complaint likho:\n")
    complaint = input("> ")
    run_pipeline(complaint)