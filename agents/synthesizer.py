import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import SecretStr

# Charge les variables d'environnement locales (.env)
load_dotenv()

def get_synthesizer_llm():
    """Récupère proprement la clé API Groq et initialise ChatGroq."""
    api_key = None
    
    # 1. Vérification dans Streamlit Secrets
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    # 2. Fallback sur les variables d'environnement (.env)
    else:
        api_key = os.environ.get("GROQ_API_KEY")

    # 3. Validation
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY est introuvable ! "
            "Vérifiez vos secrets Streamlit Cloud ou votre fichier .env local."
        )

    clean_api_key = str(api_key).strip()
    os.environ["GROQ_API_KEY"] = clean_api_key

    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=SecretStr(clean_api_key)
    )

def synthesizer_node(state):
    lang = state.get("language", "french")
    scores = state.get("expert_scores", {})
    
    llm = get_synthesizer_llm()
    
    title_example = {
        "french": "Start with a funny archetype title in French using Markdown headers (e.g., '# Archétype: LE CLOWN DE LA MATRICE').",
        "english": "Start with a funny archetype title in English using Markdown headers (e.g., '# Archetype: THE CLOWN OF THE MATRIX').",
        "arabic": "Start with a funny archetype title in Arabic using Markdown headers (e.g., '# النمط: مهرج الماتريكس')."
    }
    
    lang_instructions = {
        "french": "Write a brutal, hilarious, and accurate psychological evaluation ('Roast') of this person entirely in FRENCH.",
        "english": "Write a brutal, hilarious, and accurate psychological evaluation ('Roast') of this person entirely in ENGLISH.",
        "arabic": "Write a brutal, hilarious, and accurate psychological evaluation ('Roast') of this person entirely in ARABIC."
    }
    
    selected_title = title_example.get(lang, title_example["french"])
    selected_lang_instr = lang_instructions.get(lang, lang_instructions["french"])
    
    prompt = (
        f"You are the 'Grand Synthesizer'. Based on these scores: {scores},\n"
        f"{selected_lang_instr}\n"
        f"{selected_title}"
    )
    
    response = llm.invoke(prompt)
    return {"final_portrait": str(response.content)}