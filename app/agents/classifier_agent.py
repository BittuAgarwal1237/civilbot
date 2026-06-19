from app.llm.groq_client import llm
from app.models.outputs import ClassifierOutput

structured_llm = llm.with_structured_output(
    ClassifierOutput
)

def classifier_agent(text: str) -> ClassifierOutput:

    prompt = f"""
You are an expert civic complaint classifier.

Categories:
- Water Supply
- Electricity
- Road Maintenance
- Sanitation
- Public Safety
- Other

Examples:

Water leakage -> Water Supply
No water supply -> Water Supply

Street light not working -> Electricity
Power cut -> Electricity

Pothole on road -> Road Maintenance
Road damaged -> Road Maintenance

Garbage not collected -> Sanitation
Drain blockage -> Sanitation

Open manhole -> Public Safety
Exposed electric wire -> Public Safety

The complaint may be written in:
- English
- Hindi
- Hinglish
- Broken English
- Typo-filled text

Return:
- category
- issue_type
- urgency (1-5)

Complaint:
{text}
"""

    return structured_llm.invoke(prompt)