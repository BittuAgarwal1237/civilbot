import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm import call_llm
from utils.Storage import save_trace

SYSTEM_PROMPT = """You are an evidence extractor for Indian civic complaints.
Extract structured evidence from the complaint text and return ONLY valid JSON — no extra text, no markdown.

JSON format:
{
  "dates": ["list of dates or durations mentioned"],
  "people": ["names of people mentioned"],
  "locations": ["specific locations, areas, addresses"],
  "amounts": ["any money amounts or quantities"],
  "organizations": ["departments, offices, companies mentioned"],
  "legal_refs": ["any law, act, section mentioned"],
  "previous_complaints": ["any prior complaint references or ticket numbers"],
  "key_facts": ["3-5 most important facts from complaint"],
  "evidence_strength": 1-5
}

Evidence strength scale:
1 = Very weak (vague complaint, no details)
2 = Weak (some details)
3 = Medium (dates or locations present)
4 = Strong (multiple verifiable facts)
5 = Very strong (dates + people + location + prior complaint all present)"""


def extract_evidence(complaint_text, complaint_id):
    print("\n📋 Agent 2: Evidence Extractor running...")
    start = time.time()

    prompt = f"""Extract all evidence from this complaint:

{complaint_text}

Return only JSON."""

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
    
    # Find JSON object
    start_idx = clean.find("{")
    end_idx = clean.rfind("}") + 1
    if start_idx != -1 and end_idx > start_idx:
        clean = clean[start_idx:end_idx]

    result = json.loads(clean)

    # Save trace
    save_trace(
        complaint_id=complaint_id,
        agent_name="evidence_extractor",
        input_data=complaint_text,
        output_data=result,
        confidence=result.get("evidence_strength", 0) / 5,
        duration_ms=duration
    )

    print(f"   ✅ Key facts found: {len(result.get('key_facts', []))}")
    print(f"   ✅ Locations: {result.get('locations', [])}")
    print(f"   ✅ Dates/Duration: {result.get('dates', [])}")
    print(f"   ✅ Orgs mentioned: {result.get('organizations', [])}")
    print(f"   ✅ Evidence strength: {result.get('evidence_strength', 0)}/5")
    print(f"   ✅ Done in {duration}ms")

    return result


if __name__ == "__main__":
    print("=== Evidence Extractor Test ===")
    print("Complaint likho:")
    user_input = input("> ")

    # Dummy complaint_id for testing
    result = extract_evidence(user_input, complaint_id=1)

    print("\n📋 Full Evidence:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
   