from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from app.models.complaint import ComplaintRequest
from app.graph.workflow import workflow
from app.repositories.complaint_repository import save_complaint
from app.agents.letter_agent import letter_agent
from app.models.request import LetterRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home():
    return {
        "message": "Civic Copilot V2 Running"
    }


@app.get("/chat")
def chat_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/complaint")
def submit_complaint(request: ComplaintRequest):

    result = workflow.invoke({
        "complaint": request.complaint
    })

    print("\n========== FINAL RESULT ==========")
    print(result)

    complaint_id = save_complaint(result)

    result.pop("_id", None)

    return {
        "id": complaint_id,
        "result": result
    }


@app.post("/generate-letter")
def generate_letter(request: LetterRequest):

    try:

        result = letter_agent(
            issue_type=request.issue_type,
            location=request.location,
            department=request.department,
            user=request.user
        )

        print(result)

        department = request.department

        email = ""

        if department == "Electricity":
            email = "ce.dgvcl@gebmail.com"

        elif department == "Water Supply":
            email = "commissioner@suratmunicipal.gov.in"

        elif department == "Road Maintenance":
            email = "commissioner@suratmunicipal.gov.in"

        elif department == "Sanitation":
            email = "commissioner@suratmunicipal.gov.in"

        elif department == "Public Safety":
            email = "commissioner@suratmunicipal.gov.in"

        else:
            email = ""

        return {
            "to": email,
            "subject": result.subject,
            "letter": result.letter
        }

    except Exception as e:

        print("\n========== LETTER ERROR ==========")
        print(str(e))

        return {
            "error": str(e)
        }