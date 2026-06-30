import os
from langchain_groq import ChatGroq

def host_node(state):
    history = state["messages"]
    lang = state.get("language", "french") # "french" par défaut par sécurité
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    
    transcript = ""
    for msg in history:
        role = "User" if msg["role"] == "user" else "Host"
        transcript += f"{role}: {msg['content']}\n"
    
    # 1. Base du prompt en anglais
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
    
    # 2. Ajout de la contrainte linguistique stricte
    lang_instructions = {
        "french": "\nCRITICAL INSTRUCTION: You must output your entire response in FRENCH. Adapt your sarcastic and witty style to a natural, casual French language.",
        "english": "\nCRITICAL INSTRUCTION: You must output your entire response in ENGLISH. Keep it casual and engaging.",
        "arabic": "\nCRITICAL INSTRUCTION: You must output your entire response in ARABIC (Modern Standard Arabic). Keep it smooth, witty, and engaging."
    }
    
    prompt = base_prompt + lang_instructions[lang]
    response = llm.invoke(prompt)
    
    # Correction importante pour LangGraph + operator.add : on renvoie juste la nouveauté dans une liste
    return {
        "messages": [{"role": "assistant", "content": str(response.content)}],
        "question_count": state["question_count"] + 1
    }