import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import SecretStr

load_dotenv()

def get_groq_api_key():
    """Récupère la clé API depuis Streamlit Secrets ou l'environnement local."""
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

def get_host_llm():
    clean_api_key = get_groq_api_key()
    os.environ["GROQ_API_KEY"] = clean_api_key

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.7,
        api_key=SecretStr(clean_api_key)
    )

def host_node(state):
    """Nœud principal Host gérant les questions et le dialogue."""
    messages = state.get("messages", [])
    question_count = state.get("question_count", 0)
    lang = state.get("language", "english")

    llm = get_host_llm()

    lang_instructions = {
        "french": "Pose une question engageante et intrigante en FRANÇAIS pour analyser la personnalité de l'utilisateur.",
        "english": "Ask an engaging and intriguing question in ENGLISH to analyze the user's personality.",
        "arabic": "اطرح سؤالاً ممتعاً ومثيراً للاهتمام باللغة العربية لتحليل شخصية المستخدم."
    }

    selected_instr = lang_instructions.get(lang, lang_instructions["english"])

    system_prompt = (
        "You are the Host of an AI Personality Scanner podcast/interview.\n"
        f"Question count so far: {question_count}/4.\n"
        f"Instruction: {selected_instr}\n"
        "Keep your response concise and conversational."
    )

    prompt_messages = [("system", system_prompt)]
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
        else:
            role = getattr(msg, "type", "user")
            content = getattr(msg, "content", "")
        
        role_name = "human" if role in ["user", "human"] else "assistant"
        prompt_messages.append((role_name, content))

    response = llm.invoke(prompt_messages)
    
    new_messages = list(messages)
    new_messages.append({"role": "assistant", "content": str(response.content)})

    return {
        "messages": new_messages,
        "question_count": question_count + 1
    }