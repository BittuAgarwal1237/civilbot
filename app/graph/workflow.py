from langgraph.graph import StateGraph, END

from app.graph.nodes import (
    classifier_node,
    evidence_node,
    router_node,
    response_node,
    task_node,
    letter_node
)

graph = StateGraph(dict)

graph.add_node("classifier", classifier_node)
graph.add_node("evidence", evidence_node)
graph.add_node("router", router_node)
graph.add_node("response", response_node)
graph.add_node("task", task_node)
graph.add_node("letter", letter_node)

graph.set_entry_point("classifier")

graph.add_edge("classifier", "evidence")
graph.add_edge("evidence", "router")
graph.add_edge("router", "response")
graph.add_edge("response", "task")
graph.add_edge("task", "letter")
graph.add_edge("letter", END)

workflow = graph.compile()