import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

def get_groq_api_key():
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return str(api_key).strip()
        
    raise ValueError(
        "GROQ_API_KEY est introuvable ! "
        "Ajoutez la clé dans Secrets sur Streamlit Cloud ou dans votre fichier .env local."
    )

def get_synthesizer_llm():
    clean_api_key = get_groq_api_key()
    os.environ["GROQ_API_KEY"] = clean_api_key

    return ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.5,
        api_key=SecretStr(clean_api_key)
    )

def synthesizer_node(state):
    """Synthétise les retours de tous les experts en un portrait final."""
    expert_scores = state.get("expert_scores", {})
    lang = state.get("language", "english")
    
    llm = get_synthesizer_llm()
    
    reviews_summary = ""
    for expert, data in expert_scores.items():
        analysis = data.get("analysis", "") if isinstance(data, dict) else str(data)
        reviews_summary += f"--- {expert.upper()} EXPERT ---\n{analysis}\n\n"

    lang_instructions = {
        "french": "Rédige le portrait final entièrement en FRANÇAIS. Sois élégant, structuré et perspicace.",
        "english": "Write the final portrait entirely in ENGLISH. Make it structured, elegant, and insightful.",
        "arabic": "اكتب التقرير النهائي باللغة العربية الفصحى. اجعله منظماً وأنيقاً ومبصراً."
    }

    selected_instr = lang_instructions.get(lang, lang_instructions["english"])

    system_prompt = (
        "You are the Master Synthesizer of an AI Personality Scanner.\n"
        "Your job is to read all the expert evaluations and create a cohesive, striking, and comprehensive final personality portrait of the user.\n\n"
        f"EXPERT EVALUATIONS:\n{reviews_summary}\n\n"
        f"INSTRUCTION: {selected_instr}"
    )

    response = llm.invoke([("system", system_prompt)])

    return {
        "final_portrait": str(response.content)
    }