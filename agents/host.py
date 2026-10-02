import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import SecretStr

# Charge les variables d'environnement locales (.env)
load_dotenv()

def get_host_llm():
    """Récupère proprement la clé API Groq depuis Streamlit Secrets ou l'environnement local .env."""
    api_key = None
    
    # 1. Vérification dans Streamlit Secrets
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    # 2. Fallback sur les variables d'environnement (.env)
    else:
        api_key = os.environ.get("GROQ_API_KEY")

    # 3. Validation explicite pour éviter les erreurs
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY est introuvable ! "
            "Vérifiez vos secrets Streamlit Cloud ou votre fichier .env local."
        )

    # Nettoyage de la clé
    clean_api_key = str(api_key).strip()

    # Définition de la variable d'environnement au cas où
    os.environ["GROQ_API_KEY"] = clean_api_key

    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=SecretStr(clean_api_key)  # Conversion en SecretStr pour Pylance
    )

def host_node(state):
    history = state.get("messages", [])
    lang = state.get("language", "english")
    
    llm = get_host_llm()
    
    # Formatage de l'historique (compatible dictionnaires ET objets LangChain HumanMessage/AIMessage)
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
    
    # Prompt de base de l'hôte
    base_prompt = (
        "You are 'The Host', a witty, slightly sarcastic, and deeply observant AI interviewer. "
        "Your job is to ask the user 1 single open-ended, unexpected question to test their personality. "
        "Do not ask cliché questions. Ask about weird scenarios.\n\n"
        f"Here is the current conversation transcript:\n{transcript}\n"
        "INSTRUCTION:\n"
        "If the transcript above is empty, welcome the user and ask the very first question.\n"
        "If the user has replied, acknowledge it with a brief, sharp, or funny remark before asking the NEXT unique question.\n"
        "Do not repeat questions."
    )
    
    # Directives linguistiques
    lang_instructions = {
        "french": "\nCRITICAL INSTRUCTION: You must output your entire response in FRENCH. Adapt your sarcastic and witty style to a natural, casual French language.",
        "english": "\nCRITICAL INSTRUCTION: You must output your entire response in ENGLISH. Keep it casual and engaging.",
        "arabic": "\nCRITICAL INSTRUCTION: You must output your entire response in ARABIC (Modern Standard Arabic). Keep it smooth, witty, and engaging."
    }
    
    # Sélection de la langue avec fallback "english"
    lang_instruction = lang_instructions.get(lang, lang_instructions["english"])
    prompt = base_prompt + lang_instruction
    
    response = llm.invoke(prompt)
    
    return {
        "messages": [{"role": "assistant", "content": str(response.content)}],
        "question_count": state.get("question_count", 0) + 1
    }