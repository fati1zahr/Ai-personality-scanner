import streamlit as st
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (.env local)
load_dotenv()

# Import du graphe et éventuellement du type de State si défini dans graph_logic
from graph_logic import create_graph, ProjectState

# Configuration de la page Streamlit
st.set_page_config(
    page_title="AI Personality Scanner",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Personality Scanner")
st.markdown(
    "Répondez aux questions de l'**Host**. Après 4 questions, nos 4 experts analyseront vos réponses pour générer votre **portrait de personnalité final** !"
)

# -------------------------------------------------------------------
# INITIALISATION DU GRAPH ET DE L'ÉTAT (SESSION STATE)
# -------------------------------------------------------------------

@st.cache_resource
def load_app_graph():
    return create_graph()

graph = load_app_graph()

# Initialisation des variables de session (corrigé)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "expert_scores" not in st.session_state:
    st.session_state.expert_scores = {}
if "final_portrait" not in st.session_state:
    st.session_state.final_portrait = None
if "language" not in st.session_state:
    st.session_state.language = "french"

# -------------------------------------------------------------------
# SIDEBAR : OPTIONS & RÉINITIALISATION
# -------------------------------------------------------------------

with st.sidebar:
    st.header("⚙ Paramètres")
    
    # Choix de la langue
    selected_lang = st.selectbox(
        "Langue de l'interview :",
        options=["french", "english", "arabic"],
        index=0,
        format_func=lambda x: {"french": "🇫🇷 Français", "english": "🇬🇧 English", "arabic": "🇸🇦 العربية"}[x]
    )
    st.session_state.language = selected_lang

    st.markdown("---")
    st.write(f"📊 **Questions posées :** {st.session_state.question_count}/4")
    
    # Bouton de réinitialisation
    if st.button("🔄 Recommencer l'interview", use_container_width=True):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.expert_scores = {}
        st.session_state.final_portrait = None
        st.rerun()

# -------------------------------------------------------------------
# PREMIER LANCEMENT (Appel du Host pour la 1ère question)
# -------------------------------------------------------------------

if len(st.session_state.messages) == 0:
    with st.spinner("Invocation de l'Host..."):
        # Explicitly typed using ProjectState or cast
        initial_state: ProjectState = {
            "messages": [],
            "question_count": 0,
            "expert_scores": {},
            "final_portrait": "",
            "language": st.session_state.language
        }
        output = graph.invoke(initial_state)
        
        st.session_state.messages = output.get("messages", [])
        st.session_state.question_count = output.get("question_count", 1)

# -------------------------------------------------------------------
# AFFICHAGE DU CHAT / HISTORIQUE
# -------------------------------------------------------------------

for msg in st.session_state.messages:
    if isinstance(msg, dict):
        role = msg.get("role", "user")
        content = msg.get("content", "")
    else:
        role = "user" if getattr(msg, "type", "") in ["user", "human"] else "assistant"
        content = getattr(msg, "content", "")

    avatar = "👤" if role == "user" else "🎙️"
    with st.chat_message(role, avatar=avatar):
        st.write(content)

# -------------------------------------------------------------------
# INTERACTION UTILISATEUR & EXÉCUTION DU GRAPH
# -------------------------------------------------------------------

# Si le portrait n'est pas encore généré, on laisse l'utilisateur répondre
if not st.session_state.final_portrait:
    user_input = st.chat_input("Saisissez votre réponse ici...")

    if user_input:
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Préparation de l'état avec le type explicite
        current_state: ProjectState = {
            "messages": st.session_state.messages,
            "question_count": st.session_state.question_count,
            "expert_scores": st.session_state.expert_scores,
            "final_portrait": st.session_state.final_portrait or "",
            "language": st.session_state.language
        }

        # Exécution du graphe
        with st.spinner("Analyse de votre réponse par l'Host et les Experts..."):
            updated_state = graph.invoke(current_state)

        # Mise à jour de la session
        st.session_state.messages = updated_state.get("messages", st.session_state.messages)
        st.session_state.question_count = updated_state.get("question_count", st.session_state.question_count)
        st.session_state.expert_scores = updated_state.get("expert_scores", st.session_state.expert_scores)
        st.session_state.final_portrait = updated_state.get("final_portrait", None)

        st.rerun()

# -------------------------------------------------------------------
# AFFICHAGE DU PORTRAIT FINAL ET ANALYSES DES EXPERTS
# -------------------------------------------------------------------

if st.session_state.final_portrait:
    st.markdown("---")
    st.header("🎯 Votre Portrait de Personnalité Final")
    st.success(st.session_state.final_portrait)

    # Affichage optionnel des détails des experts
    with st.expander("🔍 Voir les détails des analyses par Expert"):
        scores = st.session_state.expert_scores
        for expert_name, data in scores.items():
            st.subheader(f"Expert : {expert_name.capitalize()}")
            if isinstance(data, dict):
                st.write(data.get("analysis", ""))
            else:
                st.write(str(data))