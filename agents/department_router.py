import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm import call_llm
from utils.Storage import save_trace


def load_departments():
    with open("data/departments.json", "r", encoding="utf-8") as f:
        return json.load(f)


SYSTEM_PROMPT = """You are a government department routing expert for India.
Given the issue type and evidence, find the correct department and return ONLY valid JSON — no extra text.

JSON format:
{
  "department": "exact department name",
  "officer": "officer designation to address",
  "escalation_officer": "senior officer if no response",
  "act": "relevant act name",
  "section": "relevant section",
  "sla_days": number,
  "contact": "helpline or portal",
  "routing_reason": "one line why this department",
  "confidence": 0.0-1.0,
  "escalate_immediately": true/false
}

escalate_immediately = true only if urgency >= 4 OR sla_days <= 3"""


def route_department(complaint_id, issue_type, urgency, evidence):
    print("\n🏛️  Agent 3: Department Router running...")
    start = time.time()

    # Step 1 — Direct lookup from departments.json
    departments = load_departments()
    dept_info = departments.get(issue_type)

    if dept_info and urgency < 4:
        # High confidence direct match — no LLM needed
        duration = int((time.time() - start) * 1000)

        result = {
            "department": dept_info["department"],
            "officer": dept_info["officer"],
            "escalation_officer": dept_info["escalation_officer"],
            "act": dept_info["act"],
            "section": dept_info["section"],
            "sla_days": dept_info["sla_days"],
            "contact": dept_info["contact"],
            "routing_reason": f"Direct match from knowledge base for {issue_type}",
            "confidence": 0.95,
            "escalate_immediately": urgency >= 4
        }

        save_trace(
            complaint_id=complaint_id,
            agent_name="department_router",
            input_data={"issue_type": issue_type, "urgency": urgency},
            output_data=result,
            confidence=0.95,
            duration_ms=duration
        )

        print(f"   ✅ Department: {result['department']}")
        print(f"   ✅ Officer: {result['officer']}")
        print(f"   ✅ Act: {result['act']} — {result['section']}")
        print(f"   ✅ SLA: {result['sla_days']} days")
        print(f"   ✅ Escalate immediately: {result['escalate_immediately']}")
        print(f"   ✅ Done in {duration}ms (direct lookup)")

        return result

    # Step 2 — LLM fallback for unknown/complex cases
    print("   ℹ️  Complex case — using LLM for routing...")

    dept_context = json.dumps(departments, indent=2)

    prompt = f"""Issue type: {issue_type}
Urgency: {urgency}/5
Key facts: {json.dumps(evidence.get('key_facts', []))}
Organizations mentioned: {json.dumps(evidence.get('organizations', []))}

Available departments:
{dept_context}

Find the best department match and return JSON."""

    response = call_llm(prompt, system_prompt=SYSTEM_PROMPT)
    duration = int((time.time() - start) * 1000)

    # Clean response
    clean = response.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            part = part.strip()
            if part.startswith("{"):
                clean = part
                break

    start_idx = clean.find("{")
    end_idx = clean.rfind("}") + 1
    if start_idx != -1 and end_idx > start_idx:
        clean = clean[start_idx:end_idx]

    result = json.loads(clean)

    save_trace(
        complaint_id=complaint_id,
        agent_name="department_router",
        input_data={"issue_type": issue_type, "urgency": urgency},
        output_data=result,
        confidence=result.get("confidence", 0.7),
        duration_ms=duration
    )

    print(f"   ✅ Department: {result['department']}")
    print(f"   ✅ Officer: {result['officer']}")
    print(f"   ✅ SLA: {result['sla_days']} days")
    print(f"   ✅ Escalate immediately: {result.get('escalate_immediately', False)}")
    print(f"   ✅ Done in {duration}ms (LLM routing)")

    return result


if __name__ == "__main__":
    print("=== Department Router Test ===")

    # Test with sample data
    test_cases = [
        {"issue_type": "water", "urgency": 3},
        {"issue_type": "electricity", "urgency": 5},
        {"issue_type": "road", "urgency": 2},
        {"issue_type": "rti", "urgency": 1},
    ]

    departments = load_departments()

    for tc in test_cases:
        print(f"\n--- Testing: {tc['issue_type']} (urgency {tc['urgency']}) ---")
        result = route_department(
            complaint_id=1,
            issue_type=tc["issue_type"],
            urgency=tc["urgency"],
            evidence={"key_facts": [], "organizations": []}
        )
        print(f"   → {result['department']} | SLA: {result['sla_days']} days | Escalate: {result['escalate_immediately']}")