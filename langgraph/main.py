from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    hello: str


graph_builder = StateGraph(State)


def node_one(state: State):
    print("node_one")


def node_two(state: State):
    print("node_two")


def node_three(state: State):
    print("node_three")


graph_builder.add_node("node_one", node_one)
graph_builder.add_node("node_two", node_two)
graph_builder.add_node("node_three", node_three)

graph_builder.add_edge(START, "node_one")
graph_builder.add_edge("node_one", "node_two")
graph_builder.add_edge("node_two", "node_three")
graph_builder.add_edge("node_three", END)

graph = graph_builder.compile()
graph.invoke({})
