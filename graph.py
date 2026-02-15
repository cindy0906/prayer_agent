from langgraph.graph import StateGraph, END
from typing import TypedDict
from nodes.analyze import analyze_text
from nodes.verse_selector import select_verse
from nodes.prayer import generate_prayer

class AgentState(TypedDict):
    emotion: str
    event: str
    verse: str
    prayer: str

graph = StateGraph(AgentState)

graph.add_node("analyze", analyze_text)
graph.add_node("verse_selector", select_verse)
graph.add_node("prayer", generate_prayer)

graph.set_entry_point("analyze")

graph.add_edge("analyze", "verse_selector")
graph.add_edge("verse_selector", "prayer")
graph.add_edge("prayer", END)

app = graph.compile()
