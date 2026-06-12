import json
import time
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm import call_llm
from utils.Storage import save_trace

SYSTEM_PROMPT_HINDI = """Aap ek senior legal aid officer hain jo Indian citizens ke liye sarkari complaints aur RTI letters likhte hain.
Aapko ek formal, legally correct Hindi letter likhna hai.

Letter mein yeh zaroor hona chahiye:
1. Sender ka address (complaint details se)
2. Date
3. Receiver — Officer ka naam aur department
4. Subject line — ek line mein issue
5. Main body — 3 paragraphs:
   - Para 1: Samasya ka vivaran (evidence ke saath)
   - Para 2: Pehle ki gayi shikayat ka reference (agar ho)
   - Para 3: Maang — kya chahiye, kab tak
6. Legal section ka reference
7. Formal closing
8. Complainant ka naam

Sirf letter likho — koi explanation nahi."""

SYSTEM_PROMPT_ENGLISH = """You are a senior legal aid officer writing formal government complaints and RTI applications for Indian citizens.
Write a formal, legally correct English letter.

Letter must include:
1. Sender address (from complaint details)
2. Date
3. Receiver — Officer name and department
4. Subject line — one line summary
5. Main body — 3 paragraphs:
   - Para 1: Description of problem with evidence
   - Para 2: Reference to previous complaint (if any)
   - Para 3: Demand — what is needed and by when
6. Legal section reference
7. Formal closing
8. Complainant name

Write only the letter — no explanation."""


def draft_response(complaint_id, complaint_text, classifier_result,
                   evidence, dept_result):
    print("\n✍️  Agent 4: Response Drafter running...")
    start = time.time()

    language = classifier_result.get("language", "english")
    issue_type = classifier_result.get("issue_type", "general")
    today = datetime.now().strftime("%d %B %Y")
    deadline = (datetime.now() + timedelta(
        days=dept_result.get("sla_days", 30)
    )).strftime("%d %B %Y")

    # Choose letter type
    if issue_type == "rti":
        letter_type = "RTI Application"
    elif dept_result.get("escalate_immediately"):
        letter_type = "Urgent Grievance Letter"
    else:
        letter_type = "Grievance Letter"

    print(f"   ℹ️  Drafting: {letter_type} in {language}")

    # Build prompt
    prompt = f"""Write a {letter_type} with these details:

COMPLAINT: {complaint_text}

EVIDENCE EXTRACTED:
- Key facts: {json.dumps(evidence.get('key_facts', []), ensure_ascii=False)}
- Dates: {json.dumps(evidence.get('dates', []), ensure_ascii=False)}
- Locations: {json.dumps(evidence.get('locations', []), ensure_ascii=False)}
- People: {json.dumps(evidence.get('people', []), ensure_ascii=False)}
- Organizations: {json.dumps(evidence.get('organizations', []), ensure_ascii=False)}
- Previous complaints: {json.dumps(evidence.get('previous_complaints', []), ensure_ascii=False)}

DEPARTMENT DETAILS:
- Department: {dept_result.get('department')}
- Officer: {dept_result.get('officer')}
- Act: {dept_result.get('act')}
- Section: {dept_result.get('section')}
- SLA: {dept_result.get('sla_days')} days

TODAY: {today}
RESPONSE DEADLINE: {deadline}

Write the complete formal letter now."""

    # Select system prompt
    if language == "hindi":
        system = SYSTEM_PROMPT_HINDI
    else:
        system = SYSTEM_PROMPT_ENGLISH

    letter = call_llm(prompt, system_prompt=system)
    duration = int((time.time() - start) * 1000)

    result = {
        "letter_type": letter_type,
        "language": language,
        "letter_text": letter,
        "addressed_to": dept_result.get("officer"),
        "department": dept_result.get("department"),
        "legal_reference": f"{dept_result.get('act')} — {dept_result.get('section')}",
        "response_deadline": deadline,
        "generated_at": today
    }

    save_trace(
        complaint_id=complaint_id,
        agent_name="response_drafter",
        input_data={
            "issue_type": issue_type,
            "language": language,
            "letter_type": letter_type
        },
        output_data={
            "letter_type": letter_type,
            "language": language,
            "addressed_to": result["addressed_to"],
            "legal_reference": result["legal_reference"]
        },
        confidence=0.9,
        duration_ms=duration
    )

    print(f"   ✅ Letter type: {letter_type}")
    print(f"   ✅ Language: {language}")
    print(f"   ✅ Addressed to: {result['addressed_to']}")
    print(f"   ✅ Legal ref: {result['legal_reference']}")
    print(f"   ✅ Deadline: {deadline}")
    print(f"   ✅ Done in {duration}ms")

    return result


if __name__ == "__main__":
    print("=== Response Drafter Test ===")
    print("Complaint likho:")
    complaint = input("> ")

    # Sample data for testing
    classifier_result = {
        "issue_type": "water",
        "urgency": 4,
        "language": "hindi"
    }

    evidence = {
        "key_facts": [
            "5 din se paani nahi aa raha",
            "50 families affected",
            "AMC ko pehle bhi complaint ki thi"
        ],
        "dates": ["pichhle 5 din se"],
        "locations": ["Ward 12, Satellite, Ahmedabad"],
        "people": [],
        "organizations": ["AMC"],
        "previous_complaints": []
    }

    dept_result = {
        "department": "Municipal Corporation / AMC",
        "officer": "Water Supply Officer",
        "escalation_officer": "Municipal Commissioner",
        "act": "Water Supply and Sewerage Act",
        "section": "Section 49",
        "sla_days": 7,
        "escalate_immediately": True
    }

    result = draft_response(
        complaint_id=1,
        complaint_text=complaint,
        classifier_result=classifier_result,
        evidence=evidence,
        dept_result=dept_result
    )

    print("\n" + "="*50)
    print("📄 GENERATED LETTER:")
    print("="*50)
    print(result["letter_text"])
    print("="*50)