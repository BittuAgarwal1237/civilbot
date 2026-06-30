from app.llm.groq_client import llm
from app.models.outputs import ClassifierOutput

structured_llm = llm.with_structured_output(
    ClassifierOutput
)

def classifier_agent(text: str) -> ClassifierOutput:

    prompt =  f"""
You are an expert civic complaint classifier.

The complaint may be written in:
- English
- Hindi
- Hinglish
- Gujarati
- Broken English
- Typo-filled text

Understand the user's intent regardless of language.

Always classify into ONE of these categories only.

Categories:
- Water Supply
- Electricity
- Roads
- Garbage
- Drainage
- Gas
- Sewerage
- Street Lights
- Traffic
- Public Safety
- Pollution
- Other

Examples:

Water leakage
No water
Pipe burst
=> Water Supply

Street light not working
Power cut
Bijli nahi aa rahi
Light chali gayi
વીજળી નથી
=> Electricity

Pothole
Road broken
Road damaged
=> Roads

Garbage not collected
Dustbin overflowing
=> Garbage

Drain blocked
Drain overflow
Sewage on road
=> Drainage

Gas leakage
Gas connection problem
PNG issue
=> Gas

Open manhole
Broken footpath
Dangerous electric wire
=> Public Safety

Return ONLY:

- category
- issue_type
- urgency (1-5)

Complaint:
{text}
"""

    return structured_llm.invoke(prompt)