from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

class AgentScore(BaseModel):
    score: int = Field(description="Rating from 1 to 10 on how much the user fits this trait.")
    justification: str = Field(description="A witty, sharp, and slightly roasting explanation of the score.")
    key_quote: str = Field(description="The exact quote from the user that triggered this analysis.")

# Dictionnaire pour guider la langue de la justification Pydantic
lang_guidance = {
    "french": "Write your 'justification' and analysis strictly in FRENCH.",
    "english": "Write your 'justification' and analysis strictly in ENGLISH.",
    "arabic": "Write your 'justification' and analysis strictly in ARABIC."
}

def format_messages(messages):
    """Safely format messages whether they are tuples, dicts, or LangChain objects."""
    formatted = []
    for m in messages:
        if isinstance(m, (tuple, list)):
            role, content = m[0], m[1]
        elif isinstance(m, dict):
            role = m.get("role", m.get("type", "user"))
            content = m.get("content", "")
        else:
            role = getattr(m, "type", getattr(m, "role", "user"))
            content = getattr(m, "content", str(m))
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)

def expert_comical_node(state):
    lang = state.get("language", "french")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    structured_llm = llm.with_structured_output(AgentScore)
    
    chat_history = format_messages(state["messages"])
    prompt = f"""You are the 'Comical Expert'. Rate how funny/sarcastic the user is (1-10).
{lang_guidance.get(lang, lang_guidance['french'])}

Chat history:
{chat_history}

Respond STRICTLY in JSON format with the required schema.
"""
    return {"expert_scores": {"comical": structured_llm.invoke(prompt)}}

def expert_serious_node(state):
    lang = state.get("language", "french")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    structured_llm = llm.with_structured_output(AgentScore)
    
    chat_history = format_messages(state["messages"])
    prompt = f"""You are the 'Serious Expert'. Rate how logical/serious the user is (1-10).
{lang_guidance.get(lang, lang_guidance['french'])}

Chat history:
{chat_history}

Respond STRICTLY in JSON format with the required schema.
"""
    return {"expert_scores": {"serious": structured_llm.invoke(prompt)}}

def expert_sensitive_node(state):
    lang = state.get("language", "french")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    structured_llm = llm.with_structured_output(AgentScore)
    
    chat_history = format_messages(state["messages"])
    prompt = f"""You are the 'Sensitive Expert'. Rate the user's emotional intelligence (1-10).
{lang_guidance.get(lang, lang_guidance['french'])}

Chat history:
{chat_history}

Respond STRICTLY in JSON format with the required schema.
"""
    return {"expert_scores": {"sensitive": structured_llm.invoke(prompt)}}

def expert_hardworker_node(state):
    lang = state.get("language", "french")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    structured_llm = llm.with_structured_output(AgentScore)
    
    chat_history = format_messages(state["messages"])
    prompt = f"""You are the 'Hardworker Expert'. Rate the user's hustle mindset (1-10).
{lang_guidance.get(lang, lang_guidance['french'])}

Chat history:
{chat_history}

Respond STRICTLY in JSON format with the required schema.
"""
    return {"expert_scores": {"hardworker": structured_llm.invoke(prompt)}}