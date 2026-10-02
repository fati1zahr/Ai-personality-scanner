import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

def get_expert_llm():
    """Récupère proprement la clé API Groq et initialise le modèle ChatGroq."""
    api_key = None
    
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY est introuvable ! "
            "Vérifiez vos secrets Streamlit Cloud ou votre fichier .env local."
        )

    clean_api_key = str(api_key).strip()
    os.environ["GROQ_API_KEY"] = clean_api_key

    return ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        api_key=SecretStr(clean_api_key)
    )

def expert_node(state, persona_name: str, persona_prompt: str):
    """Nœud générique pour exécuter l'analyse d'un expert spécifique."""
    history = state.get("messages", [])
    lang = state.get("language", "english")
    
    llm = get_expert_llm()
    
    transcript = ""
    for msg in history:
        if isinstance(msg, dict):
            role_str = msg.get("role", "user")
            content_str = msg.get("content", "")
        else:
            role_str = getattr(msg, "type", "user")
            content_str = getattr(msg, "content", "")
            
        role = "User" if role_str in ["user", "human"] else "Host"
        transcript += f"{role}: {content_str}\n"

    system_instruction = (
        f"You are {persona_name}. {persona_prompt}\n\n"
        f"Here is the interview transcript between the Host and the User:\n{transcript}\n"
        "Analyze the user's responses based on your domain expertise and give your feedback/insights."
    )

    lang_instructions = {
        "french": "\nCRITICAL INSTRUCTION: You must write your entire analysis and response in FRENCH.",
        "english": "\nCRITICAL INSTRUCTION: You must write your entire analysis and response in ENGLISH.",
        "arabic": "\nCRITICAL INSTRUCTION: You must write your entire analysis and response in ARABIC (Modern Standard Arabic)."
    }
    
    lang_instruction = lang_instructions.get(lang, lang_instructions["english"])
    prompt = system_instruction + lang_instruction

    response = llm.invoke(prompt)

    return {
        "expert_reviews": {
            persona_name: str(response.content)
        }
    }

# -------------------------------------------------------------------
# FONCTIONS NŒUDS EXPORTÉES POUR GRAPH_LOGIC.PY
# -------------------------------------------------------------------

def expert_comical_node(state):
    return expert_node(
        state, 
        persona_name="comical", 
        persona_prompt="You are witty, sarcastic, humorous, and look for comedy in everything."
    )

def expert_serious_node(state):
    return expert_node(
        state, 
        persona_name="serious", 
        persona_prompt="You are analytical, structured, logical, and focused strictly on facts."
    )

def expert_sensitive_node(state):
    return expert_node(
        state, 
        persona_name="sensitive", 
        persona_prompt="You are empathetic, emotional, supportive, and focus on human feelings."
    )

def expert_hardworker_node(state):
    return expert_node(
        state, 
        persona_name="hardworker", 
        persona_prompt="You are goal-oriented, ambitious, disciplined, and focused on productivity."
    )