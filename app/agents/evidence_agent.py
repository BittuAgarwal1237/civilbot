from app.llm.groq_client import llm
from app.models.outputs import EvidenceOutput

structured_llm = llm.with_structured_output(
    EvidenceOutput
)

def evidence_agent(text: str) -> EvidenceOutput:

    prompt = f"""
You are an expert civic evidence extraction agent.

Extract:

- location
- issue
- duration
- landmarks

Rules:

- landmarks must always be a list
- if landmarks are missing return []
- if location is missing return "not specified"
- if duration is missing return "not specified"
- understand English, Hindi, Hinglish, broken English and typos
- extract landmarks separately from location

Examples:

"Water leakage near Saraswati School"
→ location: near Saraswati School
→ issue: water leakage
→ landmarks: ["Saraswati School"]

"Pothole near railway station for 2 weeks"
→ location: near railway station
→ duration: 2 weeks
→ landmarks: ["railway station"]

"Mere area me 3 din se pani nahi aa raha"
→ location: mere area
→ duration: 3 days

Complaint:
{text}
"""

    return structured_llm.invoke(prompt)