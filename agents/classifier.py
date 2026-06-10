import json
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm import call_llm
from utils.Storage import save_complaint, save_trace

SYSTEM_PROMPT = """You are a civic issue classifier for India. 
Analyze the citizen complaint and return ONLY a valid JSON object — no explanation, no extra text.

JSON format:
{
  "issue_type": "water|electricity|road|rti|pension|ration|sanitation|land|hospital|school|other",
  "urgency": 1-5,
  "language": "hindi|english|mixed",
  "jurisdiction": "municipal|district|state|central",
  "confidence": 0.0-1.0,
  "reason": "one line explanation"
}

Urgency scale:
1 = Low (general inquiry)
2 = Medium (inconvenience)  
3 = High (affecting daily life)
4 = Very High (health/safety risk)
5 = Critical (immediate danger)"""

def classify(complaint_text):
    print("\n Agent 1: Classifier running...")
    start = time.time()

    # Save complaint
    complaint_id = save_complaint(complaint_text)

    prompt = f"Classify this complaint:\n\n{complaint_text}"

    response = call_llm(prompt, system_prompt=SYSTEM_PROMPT)

    duration = int((time.time() - start) * 1000)

    # Clean response — remove markdown if any
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    result = json.loads(clean)

    # Save to trace log
    save_trace(
        complaint_id=complaint_id,
        agent_name="classifier",
        input_data=complaint_text,
        output_data=result,
        confidence=result.get("confidence", 0),
        duration_ms=duration
    )

    print(f"   ✅ Issue: {result['issue_type']}")
    print(f"   ✅ Urgency: {result['urgency']}/5")
    print(f"   ✅ Language: {result['language']}")
    print(f"   ✅ Confidence: {result['confidence']}")
    print(f"   ✅ Done in {duration}ms")

    return complaint_id, result


if __name__ == "__main__":
    # Real time test
    print("=== Classifier Agent Test ===")
    print("Apni complaint likho (Enter dabao):")
    user_input = input("> ")

    complaint_id, result = classify(user_input)

    print("\n📋 Full Result:")
    print(json.dumps(result, indent=2))