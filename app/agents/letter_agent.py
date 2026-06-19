from app.llm.groq_client import llm
from app.models.outputs import LetterOutput

structured_llm = llm.with_structured_output(
    LetterOutput
)

def letter_agent(
    issue_type: str,
    location: str,
    department: str
) -> LetterOutput:

    prompt = f"""
You are an expert government complaint letter writer.

Generate a professional and formal complaint letter.

Issue Type: {issue_type}
Location: {location}
Department: {department}

Instructions:

- Create a clear and professional subject.
- Address the correct department.
- Mention the issue and location.
- Explain the inconvenience caused.
- Request immediate investigation and resolution.
- Use formal government letter language.
- End with a polite closing.
- Include ONLY:
  [Citizen Name]
- Do NOT include address, city, state, pincode, phone number, email, or date placeholders.

Return:

- subject
- letter
"""

    return structured_llm.invoke(prompt)