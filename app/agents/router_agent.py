from app.llm.groq_client import llm
from app.models.outputs import RouterOutput

structured_llm = llm.with_structured_output(
    RouterOutput
)

def router_agent(issue_type: str) -> RouterOutput:

    prompt = f"""
You are a civic complaint routing agent.

Assign the correct department for the issue.

Departments:

- Water Supply Department
- Electricity Department
- Road Maintenance Department
- Sanitation Department
- Public Safety Department
- General Civic Services

Examples:

Pipeline Leakage -> Water Supply Department
Water Supply Disruption -> Water Supply Department

Street Light Failure -> Electricity Department
Electricity Outage -> Electricity Department

Road Pothole -> Road Maintenance Department
Road Damage -> Road Maintenance Department

Waste Collection Delay -> Sanitation Department
Drainage Blockage -> Sanitation Department

Open Manhole Hazard -> Public Safety Department
Stray Animal Hazard -> Public Safety Department

Unknown issues -> General Civic Services

Issue Type:
{issue_type}

Return:
- department
- routing_reason
"""

    return structured_llm.invoke(prompt)