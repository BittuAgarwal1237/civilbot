from app.llm.groq_client import llm
from app.models.outputs import ResponseOutput

structured_llm = llm.with_structured_output(
    ResponseOutput
)

def response_agent(
    issue_type: str,
    department: str,
    urgency: int
) -> ResponseOutput:

    prompt = f"""
Generate a professional citizen response.

Issue Type: {issue_type}
Department: {department}
Urgency: {urgency}

Rules:
- Be polite and professional
- Mention the department
- Mention expected action
- Keep under 80 words

Return:
- citizen_response
"""

    return structured_llm.invoke(prompt)