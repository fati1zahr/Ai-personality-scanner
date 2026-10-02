import os
import streamlit as st
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

class AgentScore(BaseModel):
    score: int = Field(description="Rating from 1 to 10 on how much the user fits this trait.")
    justification: str = Field(description="A witty, sharp, and slightly roasting explanation of the score.")
    key_quote: str = Field(description="The exact quote from the user that triggered this analysis.")

lang_guidance = {
    "french": "Write your 'justification' and analysis strictly in FRENCH.",
    "english": "Write your 'justification' and analysis strictly in ENGLISH.",
    "arabic": "Write your 'justification' and analysis strictly in ARABIC."
}

def get_expert_llm():
    """Récupère la clé API Groq depuis Streamlit Secrets ou l'environnement."""
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=api_key # type: ignore
    )

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

def run_expert_node(state, expert_role, trait_key, description_prompt):
    """Fonction générique pour exécuter n'importe quel expert de manière sécurisée."""
    lang = state.get("language", "french")
    llm = get_expert_llm()
    
    # Forcer json_mode pour une meilleure compatibilité Groq + Pydantic
    structured_llm = llm.with_structured_output(AgentScore, method="json_mode")
    
    chat_history = format_messages(state.get("messages", []))
    guidance = lang_guidance.get(lang, lang_guidance["french"])
    
    prompt = f"""You are the '{expert_role}'. {description_prompt}
{guidance}

Chat history:
{chat_history}

Respond STRICTLY in JSON format matching this schema:
{{
  "score": int,
  "justification": "string",
  "key_quote": "string"
}}
"""
    result = structured_llm.invoke(prompt)
    return {"expert_scores": {trait_key: result}}

# Nœuds du graphe
def expert_comical_node(state):
    return run_expert_node(state, "Comical Expert", "comical", "Rate how funny/sarcastic the user is (1-10).")

def expert_serious_node(state):
    return run_expert_node(state, "Serious Expert", "serious", "Rate how logical/serious the user is (1-10).")

def expert_sensitive_node(state):
    return run_expert_node(state, "Sensitive Expert", "sensitive", "Rate the user's emotional intelligence (1-10).")

def expert_hardworker_node(state):
    return run_expert_node(state, "Hardworker Expert", "hardworker", "Rate the user's hustle mindset (1-10).")