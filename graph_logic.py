import operator
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agents.host import host_node
from agents.experts import expert_comical_node, expert_serious_node, expert_sensitive_node, expert_hardworker_node
from agents.synthesizer import synthesizer_node

load_dotenv()

def merge_scores(current: dict, update: dict) -> dict:
    if current is None:
        return update
    return {**current, **update}

# --- MIS À JOUR : AJOUT DE LANGUAGE ---
class ProjectState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]
    question_count: int                                    
    expert_scores: Annotated[Dict[str, dict], merge_scores]                    
    final_portrait: str   
    language: str  # "french", "english", ou "arabic"

def routing_logic(state: ProjectState):
    if state["question_count"] >= 4:
        return ["expert_comical", "expert_serious", "expert_sensitive", "expert_hardworker"]
    return END

def create_graph():
    workflow = StateGraph(ProjectState)
    
    workflow.add_node("host", host_node)
    workflow.add_node("expert_comical", expert_comical_node)
    workflow.add_node("expert_serious", expert_serious_node)
    workflow.add_node("expert_sensitive", expert_sensitive_node)
    workflow.add_node("expert_hardworker", expert_hardworker_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    workflow.set_entry_point("host")
    workflow.add_conditional_edges("host", routing_logic)
    
    workflow.add_edge("expert_comical", "synthesizer")
    workflow.add_edge("expert_serious", "synthesizer")
    workflow.add_edge("expert_sensitive", "synthesizer")
    workflow.add_edge("expert_hardworker", "synthesizer")
    
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()