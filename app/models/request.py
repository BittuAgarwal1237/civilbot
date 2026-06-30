from pydantic import BaseModel


class ComplaintRequest(BaseModel):
    complaint: str


# ------------------------
# User Details
# ------------------------

class UserDetails(BaseModel):
    name: str
    email: str
    phone: str
    address: str


# ------------------------
# Letter Request
# ------------------------

class LetterRequest(BaseModel):
    issue_type: str
    location: str
    department: str
    user: UserDetails

