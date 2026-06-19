from app.models.outputs import TaskOutput


TASKS = {
    "pipeline leakage": (
        "Inspect and repair pipeline leakage",
        "High",
        "24 hours"
    ),

    "water supply disruption": (
        "Investigate water supply disruption",
        "High",
        "24 hours"
    ),

    "street light failure": (
        "Repair electrical infrastructure",
        "Medium",
        "48 hours"
    ),

    "electricity outage": (
        "Repair electrical infrastructure",
        "Medium",
        "48 hours"
    ),

    "road pothole": (
        "Inspect and repair damaged road",
        "Medium",
        "3 days"
    ),

    "road damage": (
        "Inspect and repair damaged road",
        "Medium",
        "3 days"
    ),

    "waste collection delay": (
        "Deploy sanitation maintenance team",
        "Medium",
        "24 hours"
    ),

    "drainage blockage": (
        "Deploy sanitation maintenance team",
        "Medium",
        "24 hours"
    ),

    "open manhole hazard": (
        "Dispatch emergency safety inspection team",
        "High",
        "12 hours"
    ),

    "dangerous wiring": (
        "Dispatch emergency safety inspection team",
        "High",
        "12 hours"
    )
}


def task_agent(issue_type: str) -> TaskOutput:

    issue = issue_type.lower()

    for key, value in TASKS.items():

        if key in issue:

            return TaskOutput(
                task_title=value[0],
                priority=value[1],
                estimated_resolution=value[2]
            )

    return TaskOutput(
        task_title=f"Resolve {issue_type}",
        priority="Medium",
        estimated_resolution="48 hours"
    )