import streamlit as st
import plotly.graph_objects as go
from graph_logic import create_graph

st.set_page_config(page_title="AI Personality Scanner", page_icon="🎭", layout="centered")

#  BARRE LATÉRALE POUR LE CHOIX DE LA LANGUE 
st.sidebar.title("Configuration 🌐")
langue_choisie = st.sidebar.radio(
    "Choisissez votre langue / Select Language / اختر لغتك :",
    options=["Français 🇫🇷", "English 🇬🇧", "العربية 🇲🇦"],
    index=1  # Anglais par défaut
)

lang_map = {
    "Français 🇫🇷": "french",
    "English 🇬🇧": "english",
    "العربية 🇲🇦": "arabic"
}
current_lang = lang_map[langue_choisie]

st.title("🎭 The Council of Sages")
st.subheader("Who are you within the Matrix? Let's find out. (Just for fun)")
st.divider()

# INITIALISATION DE L'ÉTAT DE SESSION STREAMLIT
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {
        "messages": [],
        "question_count": 0,
        "expert_scores": {},
        "final_portrait": "",
        "language": current_lang  # Intégration dans l'état initial
    }

# Détection du changement de langue en cours de session -> Reset automatique
if "current_language" not in st.session_state:
    st.session_state.current_language = current_lang

if st.session_state.current_language != current_lang:
    st.session_state.current_language = current_lang
    st.session_state.graph_state = {
        "messages": [],
        "question_count": 0,
        "expert_scores": {},
        "final_portrait": "",
        "language": current_lang
    }
    st.rerun()

if "compiled_graph" not in st.session_state:
    st.session_state.compiled_graph = create_graph()

graph = st.session_state.compiled_graph
state = st.session_state.graph_state

# Si c'est le tout premier lancement
if len(state["messages"]) == 0:
    with st.spinner("Summoning The Host..."):
        updated_state = graph.invoke({
            "messages": [], 
            "question_count": 0, 
            "expert_scores": {}, 
            "final_portrait": "",
            "language": current_lang
        })
        st.session_state.graph_state = updated_state
        st.rerun()

# AFFICHAGE DE L'HISTORIQUE DE LA DISCUSSION
for msg in state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# INTERACTION UTILISATEUR (Jusqu'à 4 questions)
if state["question_count"] <= 4:
    placeholder_text = {
        "french": "Tapez votre réponse ici...",
        "english": "Type your answer here...",
        "arabic": "اكتب إجابتك هنا..."
    }
    
    if user_input := st.chat_input(placeholder_text[current_lang]):
        with st.chat_message("user"):
            st.write(user_input)
        
        state["messages"].append({"role": "user", "content": user_input})
        state["language"] = current_lang  # On s'assure que la langue suit toujours
        
        with st.spinner("The Host is thinking..."):
            updated_state = graph.invoke(state)
            st.session_state.graph_state = updated_state
        
        st.rerun()

# PHASE FINALE : AFFICHAGE DU VERDICT ET DU GRAPHIQUE RADAR
else:
    st.success("🎉 The interview is over! The Council of Sages has deliberated.")
    
    st.subheader("📊 Your Personality Metrics")
    scores = state["expert_scores"]
    categories = ['Comical 🎭', 'Serious 📐', 'Sensitive ❤️', 'Hardworker 🔥']
    
    # le score 
    user_scores = [
        scores['comical'].score if hasattr(scores['comical'], 'score') else scores['comical'].get('score', 5),
        scores['serious'].score if hasattr(scores['serious'], 'score') else scores['serious'].get('score', 5),
        scores['sensitive'].score if hasattr(scores['sensitive'], 'score') else scores['sensitive'].get('score', 5),
        scores['hardworker'].score if hasattr(scores['hardworker'], 'score') else scores['hardworker'].get('score', 5)
    ]
    
    categories.append(categories[0])
    user_scores.append(user_scores[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(135, 206, 250, 0.3)',
        line=dict(color='deepskyblue', width=2),
        name='Your Profile'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📜 The Ultimate Verdict")
    st.markdown(state["final_portrait"])
    
    if st.button("Reset Test 🔄"):
        st.session_state.graph_state = {
            "messages": [],
            "question_count": 0,
            "expert_scores": {},
            "final_portrait": "",
            "language": current_lang
        }
        st.rerun()