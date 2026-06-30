from app.llm.groq_client import llm
from app.models.outputs import LetterOutput

structured_llm = llm.with_structured_output(
    LetterOutput
)

def letter_agent(
    issue_type: str,
    location: str,
    department: str,
    user
) -> LetterOutput:

    prompt = f"""
You are an expert government complaint letter writer.

Generate a professional and formal complaint letter.

Citizen Details

Name: {user.name}

Email: {user.email}

Phone: {user.phone}

Address: {user.address}

Complaint Details

Issue Type: {issue_type}

Location: {location}

Department: {department}

Instructions:

- Create a clear professional subject.
- Address the correct department.
- Mention the issue and location.
- Explain the inconvenience caused.
- Request immediate action.
- Use formal government language.
- Do NOT use placeholders like [Citizen Name].
- Use the actual citizen information provided above.

End the letter exactly like this:

Sincerely,

{user.name}

Phone: {user.phone}

Email: {user.email}

Address: {user.address}

Return only:

- subject
- letter
"""

    return structured_llm.invoke(prompt)