from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  
from app.models.complaint import ComplaintRequest
from app.graph.workflow import workflow
from app.repositories.complaint_repository import save_complaint
from app.agents.letter_agent import letter_agent


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


class LetterRequest(BaseModel):
    issue_type: str
    location: str
    department: str


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
            department=request.department
        )

        print(result)

        return {
            "letter": result.letter
        }

    except Exception as e:

        print("\n========== LETTER ERROR ==========")
        print(str(e))

        return {
            "error": str(e)
        }