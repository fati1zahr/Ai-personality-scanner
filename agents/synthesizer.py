from langchain_groq import ChatGroq

def synthesizer_node(state):
    lang = state.get("language", "french")
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    scores = state["expert_scores"]
    
    # Traduction du titre de l'archetype selon la langue
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
    
    prompt = (
        f"You are the 'Grand Synthesizer'. Based on these scores: {scores},\n"
        f"{lang_instructions[lang]}\n"
        f"{title_example[lang]}"
    )
    
    response = llm.invoke(prompt)
    return {"final_portrait": str(response.content)}