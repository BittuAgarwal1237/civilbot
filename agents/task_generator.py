import json
import time
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm import call_llm
from utils.Storage import save_trace, save_tasks


def generate_tasks(complaint_id, classifier_result, dept_result, evidence):
    print("\n✅ Agent 5: Task Generator running...")
    start = time.time()

    today = datetime.now()
    sla_days = dept_result.get("sla_days", 30)
    urgency = classifier_result.get("urgency", 2)
    issue_type = classifier_result.get("issue_type", "general")

    # Dates calculate karo
    submit_date = (today + timedelta(days=1)).strftime("%d %B %Y")
    followup_date = (today + timedelta(days=sla_days)).strftime("%d %B %Y")
    escalate_date = (today + timedelta(days=sla_days + 7)).strftime("%d %B %Y")
    final_date = (today + timedelta(days=sla_days + 15)).strftime("%d %B %Y")

    # Core tasks — always present
    tasks = [
        {
            "task_no": 1,
            "action": f"Letter print karke {dept_result.get('officer')} ko submit karo",
            "due_date": submit_date,
            "responsible_officer": dept_result.get("officer"),
            "department": dept_result.get("department"),
            "escalate_to": None,
            "priority": "HIGH",
            "channel": "In-person / Speed Post"
        },
        {
            "task_no": 2,
            "action": "Letter ki photocopy apne paas rakho — receipt lena na bhoolo",
            "due_date": submit_date,
            "responsible_officer": "Self",
            "department": None,
            "escalate_to": None,
            "priority": "HIGH",
            "channel": "Self"
        },
        {
            "task_no": 3,
            "action": f"PGPortal.gov.in pe online complaint darj karo — ticket number save karo",
            "due_date": submit_date,
            "responsible_officer": "Self",
            "department": "PG Portal",
            "escalate_to": None,
            "priority": "MEDIUM",
            "channel": "Online — pgportal.gov.in"
        },
        {
            "task_no": 4,
            "action": f"{sla_days} din baad check karo — koi reply aaya?",
            "due_date": followup_date,
            "responsible_officer": dept_result.get("officer"),
            "department": dept_result.get("department"),
            "escalate_to": dept_result.get("escalation_officer"),
            "priority": "HIGH",
            "channel": "Phone / In-person"
        },
        {
            "task_no": 5,
            "action": f"Agar {sla_days} din mein jawab nahi aaya — {dept_result.get('escalation_officer')} ko escalate karo",
            "due_date": escalate_date,
            "responsible_officer": dept_result.get("escalation_officer"),
            "department": dept_result.get("department"),
            "escalate_to": "District Collector",
            "priority": "HIGH",
            "channel": "Written complaint + Speed Post"
        },
        {
            "task_no": 6,
            "action": "Agar escalation ke baad bhi koi jawab nahi — District Collector ko likhit shikayat do",
            "due_date": final_date,
            "responsible_officer": "District Collector",
            "department": "District Collectorate",
            "escalate_to": "State CM Helpline",
            "priority": "CRITICAL",
            "channel": "Written + CM Helpline"
        }
    ]

    # Urgency 4-5 pe extra immediate task
    if urgency >= 4:
        tasks.insert(0, {
            "task_no": 0,
            "action": f"URGENT: Aaj hi helpline {dept_result.get('contact', '155304')} pe call karo",
            "due_date": today.strftime("%d %B %Y"),
            "responsible_officer": dept_result.get("officer"),
            "department": dept_result.get("department"),
            "escalate_to": None,
            "priority": "CRITICAL",
            "channel": f"Helpline: {dept_result.get('contact', '155304')}"
        })

    # RTI ke liye extra task
    if issue_type == "rti":
        tasks.append({
            "task_no": len(tasks) + 1,
            "action": "30 din mein reply nahi aaya toh First Appellate Authority ke paas second appeal karo",
            "due_date": (today + timedelta(days=45)).strftime("%d %B %Y"),
            "responsible_officer": "First Appellate Authority",
            "department": dept_result.get("department"),
            "escalate_to": "Central Information Commission (CIC)",
            "priority": "HIGH",
            "channel": "Written appeal"
        })

    duration = int((time.time() - start) * 1000)

    # Save tasks
    save_tasks(complaint_id, tasks)

    # Save trace
    save_trace(
        complaint_id=complaint_id,
        agent_name="task_generator",
        input_data={
            "issue_type": issue_type,
            "urgency": urgency,
            "sla_days": sla_days
        },
        output_data={"total_tasks": len(tasks)},
        confidence=1.0,
        duration_ms=duration
    )

    print(f"   ✅ Total tasks generated: {len(tasks)}")
    print(f"   ✅ Submit by: {submit_date}")
    print(f"   ✅ Follow up by: {followup_date}")
    print(f"   ✅ Escalate by: {escalate_date}")
    if urgency >= 4:
        print(f"   🚨 URGENT task added — call helpline today!")
    print(f"   ✅ Done in {duration}ms")

    return tasks


if __name__ == "__main__":
    print("=== Task Generator Test ===\n")

    # Sample test data
    classifier_result = {
        "issue_type": "water",
        "urgency": 4,
        "language": "hindi"
    }

    dept_result = {
        "department": "Municipal Corporation / AMC",
        "officer": "Water Supply Officer",
        "escalation_officer": "Municipal Commissioner",
        "act": "Water Supply and Sewerage Act",
        "section": "Section 49",
        "sla_days": 7,
        "contact": "155303",
        "escalate_immediately": True
    }

    evidence = {
        "key_facts": ["5 din se paani nahi", "50 families affected"]
    }

    tasks = generate_tasks(
        complaint_id=1,
        classifier_result=classifier_result,
        dept_result=dept_result,
        evidence=evidence
    )

    print("\n📋 COMPLETE ACTION PLAN:")
    print("=" * 55)
    for task in tasks:
        priority_icon = "🚨" if task["priority"] == "CRITICAL" else "🔴" if task["priority"] == "HIGH" else "🟡"
        print(f"\n{priority_icon} Task {task['task_no']}: {task['action']}")
        print(f"   📅 Due: {task['due_date']}")
        print(f"   👤 To: {task['responsible_officer']}")
        print(f"   📡 Channel: {task['channel']}")
        if task.get("escalate_to"):
            print(f"   ⬆️  Escalate to: {task['escalate_to']}")
    print("=" * 55)