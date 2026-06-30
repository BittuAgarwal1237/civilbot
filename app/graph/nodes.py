from app.agents.classifier_agent import classifier_agent
from app.agents.evidence_agent import evidence_agent
from app.agents.router_agent import router_agent
from app.agents.response_agent import response_agent
from app.agents.task_agent import task_agent
from app.agents.letter_agent import letter_agent


def classifier_node(state):

    print("\n========== CLASSIFIER NODE ==========")

    result = classifier_agent(
        state["complaint"]
    )

    print("Classifier Result:", result)

    state["classification"] = result.model_dump()

    return state


def evidence_node(state):

    print("\n========== EVIDENCE NODE ==========")

    complaint = state["complaint"]

    print("Complaint:", complaint)

    result = evidence_agent(
        complaint
    )

    print("Evidence Result:", result)

    state["evidence"] = result.model_dump()

    return state


def router_node(state):

    print("\n========== ROUTER NODE ==========")

    result = router_agent(
        state["classification"]["issue_type"]
    )

    print("Router Result:", result)

    state["department"] = result.department
    state["routing_reason"] = result.routing_reason

    return state


def response_node(state):

    print("\n========== RESPONSE NODE ==========")

    result = response_agent(
        issue_type=state["classification"]["issue_type"],
        department=state["department"],
        urgency=state["classification"]["urgency"]
    )

    print("Response Result:", result)

    state["response"] = result.citizen_response

    return state


def task_node(state):

    print("\n========== TASK NODE ==========")

    result = task_agent(
        state["classification"]["issue_type"]
    )

    print("Task Result:", result)

    state["task"] = result.model_dump()

    return state
