# 🎭 The Council of Sages - AI Personality Assessment

Bienvenue dans **The Council of Sages**, une application web interactive et multilingue (Français, Anglais, Arabe) qui évalue votre personnalité à travers des questions insolites et un brin sarcastiques. 

L'application est propulsée par un système multi-agent (MAS) orchestré par **LangGraph** et exécuté à l'aide des modèles de pointe **Llama 3.3 (70B) sur Groq**.

## 🚀 Fonctionnalités
- **🌐 Multilingue :** Choisissez votre langue (🇬🇧 / 🇫🇷 / 🇲🇦) dès le départ, l'intégralité du test s'adapte automatiquement.
- **🧠 Orchestration LangGraph :** Un agent principal (*The Host*) mène l'interview. Une fois le quota de questions atteint, 4 experts spécialisés analysent vos réponses en parallèle.
- **📊 Visualisation Radar (Plotly) :** Visualisez instantanément vos scores sur un graphique radar dynamique à la fin du test.
- **📜 Le Verdict Final :** Un synthétiseur rassemble les analyses des experts pour vous proposer un profil psychologique mémorable et percutant (*Roast*).

## 🛠️ Architecture du Projet
Le projet est structuré de manière modulaire :
- `app.py` : L'interface utilisateur interactive conçue avec Streamlit.
- `graph_logic.py` : La configuration et les règles de transition du graphe LangGraph.
- `agents/` : Contient la logique de chaque agent :
  - `host.py` : L'hôte qui gère la discussion.
  - `experts.py` : Les 4 agents experts qui évaluent les critères (Comical, Serious, Sensitive, Hardworker) avec des sorties structurées Pydantic.
  - `synthesizer.py` : L'agent final qui rédige le portrait.

