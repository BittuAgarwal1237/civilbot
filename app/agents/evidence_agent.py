from app.llm.groq_client import llm
from app.models.outputs import EvidenceOutput

structured_llm = llm.with_structured_output(
    EvidenceOutput
)

def evidence_agent(text: str) -> EvidenceOutput:

    prompt = f"""
You are an expert civic evidence extraction agent.

The complaint may be written in:
- English
- Hindi
- Gujarati
- Hinglish
- Broken English
- Typo-filled text

Extract:

- location
- city
- state
- issue
- duration
- landmarks

Rules:

- landmarks must always be a list.
- If landmarks are missing return [].
- If location is missing return "not specified".
- If city cannot be determined return "not specified".
- If state cannot be determined return "not specified".
- If duration is missing return "not specified".
- Correct spelling mistakes.
- Understand mixed languages.
- Extract landmarks separately from location.

Examples:

Complaint:
Water leakage near Saraswati School.

Output:
location: near Saraswati School
city: not specified
state: not specified
issue: water leakage
duration: not specified
landmarks: ["Saraswati School"]

Complaint:
Pothole near railway station for 2 weeks.

Output:
location: near railway station
city: not specified
state: not specified
issue: pothole
duration: 2 weeks
landmarks: ["railway station"]

Complaint:
Hamare Jahangirpura area me light nahi hai 2 din se.

Output:
location: Jahangirpura
city: Surat
state: Gujarat
issue: electricity outage
duration: 2 days
landmarks: []

Complaint:
મારા વિસ્તારમાં ગેસ લીકેજ છે.

Output:
location: not specified
city: not specified
state: Gujarat
issue: gas leakage
duration: not specified
landmarks: []

Complaint:
{text}
"""
    return structured_llm.invoke(prompt)