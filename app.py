import streamlit as st
import openai
from datetime import datetime

# Configuration de la page - optimisée pour iPad
st.set_page_config(
    page_title="Mon Tuteur Math 📐",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour iPad
st.markdown("""
<style>
    /* Optimisation pour iPad */
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .stTextInput>div>div>input {
        font-size: 16px;
        padding: 15px;
    }
    
    .stTextArea>div>div>textarea {
        font-size: 16px;
        padding: 15px;
    }
    
    /* Cartes de sujets */
    .subject-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #FF4B4B;
    }
    
    /* Messages */
    .user-message {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid #90caf9;
        color: #000000;
    }
    
    .assistant-message {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid #e0e0e0;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = None
if 'api_key' not in st.session_state:
    # Essaie d'abord de charger depuis les secrets Streamlit
    try:
        st.session_state.api_key = st.secrets["OPENAI_API_KEY"]
    except:
        st.session_state.api_key = None

# Sidebar - Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # API Key - affiche seulement si pas dans les secrets
    if st.session_state.api_key:
        st.success("✅ Clé API configurée!")
        if st.button("🔄 Changer la clé API"):
            st.session_state.api_key = None
            st.rerun()
    else:
        api_key = st.text_input(
            "Clé API OpenAI",
            type="password",
            help="Entre ta clé API OpenAI"
        )
        if api_key:
            st.session_state.api_key = api_key
    
    # Configure OpenAI
    if st.session_state.api_key:
        openai.api_key = st.session_state.api_key
    
    st.divider()
    
    # Sélection du sujet
    st.subheader("📚 Sujets de Mathématiques")
    
    subjects = {
        "Exposants et notation scientifique": {
            "emoji": "🔢",
            "description": "Puissances, exposants négatifs, notation scientifique"
        },
        "Équations": {
            "emoji": "⚖️",
            "description": "Équations du 1er et 2e degré, systèmes d'équations"
        },
        "Fonctions": {
            "emoji": "📈",
            "description": "Fonctions linéaires, affines, règles de transformation"
        },
        "Géométrie": {
            "emoji": "📐",
            "description": "Théorème de Pythagore, aires, volumes, triangles semblables"
        }
    }
    
    for subject, info in subjects.items():
        if st.button(f"{info['emoji']} {subject}", use_container_width=True):
            st.session_state.current_subject = subject
            st.rerun()
    
    st.divider()
    
    # Options
    st.subheader("🎯 Préférences")
    difficulty = st.select_slider(
        "Niveau de difficulté",
        options=["Facile", "Moyen", "Difficile"],
        value="Moyen"
    )
    
    show_steps = st.checkbox("Montrer les étapes détaillées", value=True)
    
    st.divider()
    
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Fonction pour appeler OpenAI
def get_math_response(messages, subject, difficulty, show_steps):
    if not st.session_state.api_key:
        return "⚠️ Veuillez entrer votre clé API OpenAI dans la barre latérale."
    
    try:
        system_prompt = f"""Tu es un tuteur de mathématiques patient et encourageant pour des élèves de Secondaire 3 au Québec (environ 14-15 ans).

Sujet actuel: {subject}
Niveau de difficulté: {difficulty}
Montrer les étapes: {'Oui' if show_steps else 'Non'}

Directives importantes:
1. Explique en français simple et clair
2. Utilise des exemples concrets et pertinents pour des adolescents
3. {'Montre TOUTES les étapes de calcul en détail' if show_steps else 'Donne une explication concise'}
4. Encourage l'élève avec des mots positifs
5. Vérifie la compréhension en posant des questions
6. Utilise des émojis occasionnellement pour rendre ça fun 😊
7. Si l'élève fait une erreur, explique gentiment où et pourquoi
8. Adapte ton langage au niveau Secondaire 3 (pas trop complexe)
9. Pour les exposants, utilise la notation: x^2 pour x au carré
10. Fournis des astuces et raccourcis quand c'est approprié

Rappel: Tu aides des élèves du Pensionnat Saint-Nom-de-Marie à Montréal, donc sois familier avec le programme québécois de mathématiques de Secondaire 3."""

        client = openai.OpenAI(api_key=st.session_state.api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}\n\nVérifie que ta clé API est correcte."

# En-tête principal
st.title("📐 Mon Tuteur de Math")
st.markdown("### *Ton aide personnalisée pour Sec 3* ✨")

# Affichage du sujet actuel
if st.session_state.current_subject:
    subject_info = subjects[st.session_state.current_subject]
    st.info(f"{subject_info['emoji']} **Sujet actuel:** {st.session_state.current_subject}\n\n*{subject_info['description']}*")
else:
    st.warning("👈 Choisis un sujet de mathématiques dans le menu à gauche pour commencer!")

# Zone de conversation
st.markdown("---")

# Afficher l'historique des messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message"><strong>Toi:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">🤖 <strong>Tuteur:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

# Zone de saisie
st.markdown("---")

# Utilise un formulaire pour auto-clear après envoi
with st.form(key="question_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Pose ta question ou décris ton problème de math...",
            height=100,
            placeholder="Exemple: Comment je résous l'équation 2x + 5 = 13 ?",
            key="user_input"
        )
    
    with col2:
        st.write("")  # Espacement
        st.write("")  # Espacement
        send_button = st.form_submit_button("📤 Envoyer", use_container_width=True, type="primary")

# Exemples de questions
with st.expander("💡 Besoin d'inspiration? Clique ici pour voir des exemples de questions"):
    if st.session_state.current_subject == "Exposants et notation scientifique":
        st.markdown("""
        - Comment je calcule 2^5 × 2^3 ?
        - Comment j'écris 0.000045 en notation scientifique ?
        - Qu'est-ce qu'un exposant négatif ?
        - Comment je simplifie (3^4)^2 ?
        """)
    elif st.session_state.current_subject == "Équations":
        st.markdown("""
        - Comment je résous 3x - 7 = 14 ?
        - Comment je résous une équation du 2e degré ?
        - C'est quoi un système d'équations ?
        - Comment je vérifie ma réponse ?
        """)
    elif st.session_state.current_subject == "Fonctions":
        st.markdown("""
        - C'est quoi une fonction affine ?
        - Comment je trouve la pente d'une droite ?
        - Comment je trace le graphique de y = 2x + 3 ?
        - Comment les transformations affectent les fonctions ?
        """)
    elif st.session_state.current_subject == "Géométrie":
        st.markdown("""
        - Comment j'utilise le théorème de Pythagore ?
        - Comment je calcule l'aire d'un triangle ?
        - C'est quoi des triangles semblables ?
        - Comment je trouve le volume d'un cylindre ?
        """)

# Traitement de l'envoi
if send_button and user_input and st.session_state.current_subject:
    # Ajouter le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Obtenir la réponse
    with st.spinner("🤔 Je réfléchis..."):
        response = get_math_response(
            st.session_state.messages,
            st.session_state.current_subject,
            difficulty,
            show_steps
        )
    
    # Ajouter la réponse
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Recharger pour afficher les nouveaux messages
    st.rerun()

elif send_button and not st.session_state.current_subject:
    st.error("⚠️ Choisis d'abord un sujet dans le menu à gauche!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 14px;'>
    💝 Fait avec amour par ton papou pour t'aider en math! 💝<br>
    N'hésite pas à poser autant de questions que tu veux: il n'y a pas de mauvaises questions!
</div>
""", unsafe_allow_html=True)