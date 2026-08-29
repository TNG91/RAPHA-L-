import streamlit as st, requests, base64, time, re, json, uuid, hashlib
import streamlit.components.v1 as components

st.set_page_config(page_title="RAPHAËL", page_icon="✨", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');
* {font-family:'Inter', sans-serif;}

/* --- Palette façon maquette : fond clair, bulles colorées navy/lavande --- */
.stApp {background:#F4F5F9!important; color:#1A1A2E!important;}
section[data-testid="stSidebar"] {background:#ffffff!important; border-right:1px solid #E5E7EF!important;}
div[data-testid="stChatMessages"] {gap: 0.9rem!important; padding-top: 0.8rem; padding-bottom: 2rem;}

/* Message assistant : bulle lavande claire avec avatar "R" */
.stChatMessage:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background:#EDEBFB!important;
    border:none!important;
    border-radius:18px!important;
    box-shadow:none!important;
    padding: 16px 20px!important;
    max-width: 700px!important;
    margin: 0 auto!important;
}
/* Message utilisateur : bulle navy pleine, texte blanc */
.stChatMessage:has(div[data-testid="stChatMessageAvatarUser"]) {
    background:#1E2A5A!important;
    border:none!important;
    border-radius:18px!important;
    padding: 14px 20px!important;
    max-width: 640px!important;
    margin: 0 auto!important;
    box-shadow:none!important;
}
.stChatMessage:has(div[data-testid="stChatMessageAvatarUser"]) p,
.stChatMessage:has(div[data-testid="stChatMessageAvatarUser"]) li {
    color:#ffffff!important;
}
div[data-testid="stChatMessageAvatarUser"] {background:#3A4A8A!important;}
div[data-testid="stChatMessageAvatarAssistant"] {background:#1E2A5A!important;}
.stChatMessage p,.stChatMessage li {
    font-family:'Inter', sans-serif!important;
    font-size: var(--lyra-font-size, 16px)!important;
    line-height: 1.6!important;
    letter-spacing: 0.1px!important;
    color: #1A1A2E!important;
    margin-bottom: 0.4em!important;
}
.stChatMessage h1,.stChatMessage h2,.stChatMessage h3 {
    font-family:'Inter', sans-serif!important;
    font-weight:600!important;
    color:#1A1A2E!important;
    margin-top: 0.6em!important;
    margin-bottom: 0.3em!important;
}
div[data-testid="stChatInput"] {
    background:#ffffff!important;
    border:1px solid #E5E7EF!important;
    border-radius:28px!important;
    max-width: 760px!important;
    margin: 0 auto!important;
    box-shadow: 0 2px 8px rgba(30,42,90,0.06)!important;
}
div.block-container {padding-top: 0!important; padding-bottom: 0.5rem!important;}
div[data-testid="stVerticalBlock"] {gap: 0.4rem!important;}
.stPopover, .stButton, .stDownloadButton {margin: 0!important;}
hr, div[data-testid="stMarkdownContainer"] hr {margin: 0.5rem 0!important;}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {gap: 0.3rem!important;}

/* Accent navy sur les boutons et toggles */
.stButton button, .stDownloadButton button {
    border-radius:10px!important;
    border:1px solid #E5E7EF!important;
    background:#ffffff!important;
    color:#1A1A2E!important;
}
.stButton button:hover, .stDownloadButton button:hover {
    border-color:#1E2A5A!important;
    color:#1E2A5A!important;
}
.stButton button[kind="primary"] {
    background:#1E2A5A!important;
    border:1px solid #1E2A5A!important;
    color:#ffffff!important;
    font-weight:600!important;
}
.stButton button[kind="primary"]:hover {
    background:#14203F!important;
    border-color:#14203F!important;
    color:#ffffff!important;
}
.stButton button:disabled {
    background:#F0F1F6!important;
    border:1px solid #E5E7EF!important;
    color:#6B6F85!important;
    opacity:1!important;
    font-weight:600!important;
}
div[data-baseweb="checkbox"] span, .stToggle {accent-color:#1E2A5A!important;}
[data-testid="stMarkdownContainer"] a {color:#1E2A5A!important;}

.lyra-warning {
    background:#FBF0E4; border:1px solid #E3A96B; border-radius:12px;
    padding:12px 16px; color:#8A5A20; font-size:14px; margin-bottom:1rem;
}
.lyra-crisis {
    background:#FBEAE6; border:1px solid #C0392B; border-radius:12px;
    padding:14px 18px; color:#8A3A20; font-size:14px; margin-bottom:1rem; line-height:1.6;
}
.lyra-footer {
    text-align:center; color:#8B8FA3; font-size:12px; padding:1rem 0 0.5rem 0;
}
.conv-btn button {
    text-align:left!important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.raphael-header {
    background:linear-gradient(135deg,#111A3D,#1E2A5A);
    padding:2.2rem 1rem 1.6rem 1rem;
    text-align:center;
    margin:-1rem -1rem 1rem -1rem;
    border-radius:0 0 20px 20px;
}
.raphael-header .logo {
    width:64px;height:64px;border-radius:16px;
    background:linear-gradient(135deg,#3A4A8A,#1E2A5A);
    margin:0 auto 0.8rem auto;display:flex;align-items:center;justify-content:center;
    color:white;font-size:28px;font-weight:700;
    box-shadow:0 4px 16px rgba(30,42,90,0.4);
}
.raphael-header h1 {
    color:white;font-size:2.2rem;font-weight:800;letter-spacing:1px;margin:0;
}
.raphael-header p {
    color:#B8BEDC;font-size:0.95rem;margin-top:0.3rem;
}
.sujet-pill button {
    text-align:left!important; font-weight:500!important;
}
</style>
""", unsafe_allow_html=True)

# --- Thème clair (défaut, façon Claude) / sombre ---------------------------
if st.session_state.get("theme", "Clair") == "Sombre":
    st.markdown("""
    <style>
    .stApp {background:#0f0f10!important; color:#ececec!important;}
    section[data-testid="stSidebar"] {background:#18181b!important; border-right:1px solid #27272a!important;}
    .stChatMessage:has(div[data-testid="stChatMessageAvatarUser"]) {background:#232326!important;}
    .stChatMessage p,.stChatMessage li {color:#ececec!important;}
    .stChatMessage h1,.stChatMessage h2,.stChatMessage h3 {color:#fff!important;}
    div[data-testid="stChatInput"] {background:#18181b!important; border:1px solid #3f3f46!important;}
    .stButton button, .stDownloadButton button {background:#18181b!important; border:1px solid #3f3f46!important; color:#ececec!important;}
    .lyra-footer {color:#71717a!important;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CRITÈRES D'UNE BONNE IA — appliqués dans tout le fichier
# 1. Utilité & pédagogie active     6. Sécurité des mineurs & contenu approprié
# 2. Honnêteté & transparence       7. Anti-dépendance affective
# 3. Sécurité & gestion de crise    8. Robustesse technique & accessibilité
# 4. Confidentialité & sobriété     9. Limites clairement énoncées
#    des données                   10. Expérience type ChatGPT (historique de
# 5. Neutralité & absence de biais      conversations, réponse en flux, fichiers)
# ---------------------------------------------------------------------------

# --- 10. Multi-conversations façon ChatGPT ---------------------------------
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {first_id: {"title": "Nouvelle conversation", "messages": []}}
    st.session_state.current_conv = first_id
if "niveau" not in st.session_state: st.session_state.niveau = "Terminale"
if "cycle" not in st.session_state: st.session_state.cycle = "Lycée"
if "last_call" not in st.session_state: st.session_state.last_call = 0.0
if "font_size" not in st.session_state: st.session_state.font_size = "Normale"

# --- Accès gratuit et illimité pour tous ---------------------------------
import datetime as _dt

def current_messages():
    return st.session_state.conversations[st.session_state.current_conv]["messages"]

def set_conv_title_from_first_message(text):
    conv = st.session_state.conversations[st.session_state.current_conv]
    if conv["title"] == "Nouvelle conversation":
        conv["title"] = (text[:40] + "…") if len(text) > 40 else text

KEY = st.secrets.get("GROQ_API_KEY", "").strip()

# --- Base de données Supabase : DÉSACTIVÉE POUR LE MOMENT -------------------
# Comptes et conversations vivent uniquement dans la session du navigateur
# (perdus à la fermeture / au redéploiement). Pour réactiver Supabase plus
# tard : remettre SUPABASE_URL / SUPABASE_KEY ci-dessous (st.secrets) et
# restaurer les fonctions db_* d'origine.
SUPABASE_URL = ""
SUPABASE_KEY = ""

def _supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def hash_password(password):
    """Ancien schéma (SHA-256 simple, sans sel) — gardé uniquement pour vérifier
    les comptes créés avant la migration vers PBKDF2."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def make_salt():
    return uuid.uuid4().hex

def hash_password_v2(password, salt):
    """Hachage robuste : PBKDF2-HMAC-SHA256, 200 000 itérations, sel unique par compte."""
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()

def verify_password(password, student):
    """Vérifie le mot de passe en supportant les deux schémas (migration en douceur) :
    si le compte a un sel enregistré, on utilise le nouveau hachage sécurisé ; sinon on
    retombe sur l'ancien SHA-256 simple, le temps que le compte se reconnecte une fois."""
    salt = student.get("password_salt")
    if salt:
        return student.get("password_hash") == hash_password_v2(password, salt)
    return student.get("password_hash") == hash_password(password)

# --- Comptes élèves : version locale (session), Supabase désactivé --------
# Comptes et historique vivent dans st.session_state.local_students, perdus
# à la fermeture de l'onglet / au redémarrage de l'app.

def _local_students():
    if "local_students" not in st.session_state:
        st.session_state.local_students = {}
    return st.session_state.local_students

def db_get_student(email):
    return _local_students().get(email), "ok"

def db_create_student(email, password_hash, password_salt):
    student = {"email": email, "password_hash": password_hash, "password_salt": password_salt}
    _local_students()[email] = student
    return student

def db_update_student(email, **fields):
    students = _local_students()
    if email not in students:
        return False
    students[email].update(fields)
    return True

def db_save_conversations(email, conversations):
    """Sauvegarde locale (session) des conversations de l'élève."""
    try:
        payload = json.dumps(conversations)[:900000]  # garde-fou taille raisonnable
        return db_update_student(email, conversations_json=payload)
    except Exception:
        return False

def db_load_conversations(email):
    """Recharge les conversations sauvegardées d'un élève, si présentes."""
    student, status = db_get_student(email)
    if status != "ok" or not student:
        return None
    raw = student.get("conversations_json")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None

def db_list_students():
    """Récupère tous les élèves (pour les statistiques admin) — session locale."""
    return [{"email": e} for e in _local_students().keys()], "ok"

def db_export_all_students():
    """Exporte toute la base élèves de la session locale."""
    return list(_local_students().values()), "ok"

CYCLES = {
    "Collège": ["6e", "5e", "4e", "3e"],
    "Lycée": ["Seconde", "Première", "Terminale"],
    "Université": ["Licence 1", "Licence 2", "Licence 3", "Master 1", "Master 2", "Doctorat"]
}
PROGRAMMES = {
    "6e": "bases fractions, décimaux, géométrie simple", "5e": "fractions, proportionnalité", "4e": "Pythagore, Thalès, équations",
    "3e": "fonctions, racine carrée, Brevet", "Seconde": "fonctions, vecteurs", "Première": "dérivées, suites",
    "Terminale": "limites, intégrales, Bac", "Licence 1": "analyse réelle, algèbre linéaire", "Licence 2": "analyse avancée",
    "Licence 3": "topologie", "Master 1": "master recherche", "Master 2": "expert", "Doctorat": "recherche doctorale"
}
MINEUR_CYCLES = {"Collège", "Lycée"}  # utilisateurs probablement mineurs -> ton et contenu adaptés

# --- Bilingue français / anglais --------------------------------------------
# La structure du programme (Collège/Lycée/Université, Brevet/Bac) reste
# affichée dans ses noms d'origine — décision volontaire : ces repères sont
# déjà utilisés tels quels dans de nombreux pays francophones. Seule
# l'interface et le ton des réponses changent selon la langue choisie.
if "langue" not in st.session_state: st.session_state.langue = "Français"

TR = {
    "Français": {
        "tagline": "T'aide à comprendre, pas juste à trouver la réponse",
        "chat_titre": "Chat avec RAPHAËL",
        "chat_status": "🟢 En ligne",
        "new_chat": "➕ Nouveau chat",
        "sujets": "SUJETS",
        "niveau_scolaire": "🔒 Niveau scolaire",
        "verrouille": "Verrouillé sur",
        "favoris": "FAVORIS",
        "historique": "HISTORIQUE",
        "rechercher_conv": "🔍 Rechercher...",
        "aucune_conv": "Aucune conversation trouvée.",
        "deconnexion": "🚪 Se déconnecter",
        "acces_gratuit": "✅ Accès gratuit et illimité",
        "chat_placeholder": "Pose ta question à RAPHAËL...",
        "footer": "RAPHAËL peut faire des erreurs. Vérifie les informations importantes.",
        "email": "Email", "mot_de_passe": "Mot de passe",
        "connexion_btn": "Se connecter / Créer un compte",
        "mdp_oublie": "Mot de passe oublié ?",
        "err_champs": "Renseigne un email et un mot de passe.",
        "err_connexion_db": "Impossible de contacter la base de données. Réessaie dans un instant.",
        "err_mdp": "Mot de passe incorrect.",
        "err_creation": "Erreur lors de la création du compte. Réessaie.",
    },
    "English": {
        "tagline": "Helps you understand, not just find the answer",
        "chat_titre": "Chat with RAPHAËL",
        "chat_status": "🟢 Online",
        "new_chat": "➕ New chat",
        "sujets": "SUBJECTS",
        "niveau_scolaire": "🔒 Grade level",
        "verrouille": "Locked on",
        "favoris": "FAVORITES",
        "historique": "HISTORY",
        "rechercher_conv": "🔍 Search...",
        "aucune_conv": "No conversation found.",
        "deconnexion": "🚪 Log out",
        "acces_gratuit": "✅ Free and unlimited access",
        "chat_placeholder": "Ask RAPHAËL a question...",
        "footer": "RAPHAËL can make mistakes. Check important information.",
        "email": "Email", "mot_de_passe": "Password",
        "connexion_btn": "Log in / Create an account",
        "mdp_oublie": "Forgot your password?",
        "err_champs": "Please enter an email and a password.",
        "err_connexion_db": "Couldn't reach the database. Try again in a moment.",
        "err_mdp": "Incorrect password.",
        "err_creation": "Error creating the account. Please try again.",
    }
}
def t(key):
    return TR.get(st.session_state.langue, TR["Français"]).get(key, key)

# --- 3. Sécurité & gestion de crise -----------------------------------------
CRISIS_PATTERNS = [
    r"\bsuicid", r"\bme tuer\b", r"\bme faire du mal\b", r"\benvie de mourir\b",
    r"\bscarification", r"\bplus envie de vivre\b", r"\bharc[eè]l"
]

def detect_crisis(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in CRISIS_PATTERNS)

CRISIS_MESSAGE = """Ce que tu traverses semble difficile, et ça compte. Je suis une IA pédagogique et je ne suis pas la bonne ressource pour ça — mais il existe des personnes formées pour t'aider vraiment.

**En France :**
- **3114** — numéro national de prévention du suicide, gratuit, 24h/24
- **Fil Santé Jeunes : 0 800 235 236** (appel et tchat anonymes)
- Ou parle à un adulte de confiance : parent, infirmier(ère) scolaire, professeur

Tu n'as pas à traverser ça seul(e). N'hésite pas à contacter une de ces ressources."""

PRIVACY_NOTE = "RAPHAËL ne conserve tes conversations que dans ton navigateur pour cette session — rien n'est envoyé à un serveur permanent par l'application elle-même."

# --- 1, 2, 5, 6, 7, 10. Prompt système --------------------------------------
# Comportement assoupli façon ChatGPT : RAPHAËL répond volontiers à des questions
# hors programme (curiosité générale, culture, aide méthodologique...) au lieu
# de les refuser, tout en restant identifiable comme tuteur scolaire et en
# recentrant naturellement vers le niveau de l'élève quand c'est pertinent.
def system_prompt(niveau, cycle, detailed=False, sujet=None, pays=None, langue="Français"):
    prog = PROGRAMMES.get(niveau, "")
    contexte_mineur = ""
    if cycle in MINEUR_CYCLES:
        contexte_mineur = """
9. L'élève est probablement mineur : garde un contenu strictement adapté à son âge, sans aucune ambiguïté, et ne développe jamais de sujets sensibles (violence, sexualité, substances) même si la question dévie vers ça — recentre poliment sur le scolaire."""
    mode_note = ("\n\nMODE DÉTAILLÉ ACTIVÉ : développe davantage — étapes intermédiaires, exemples supplémentaires, contre-exemples si utile — sans pour autant délayer inutilement."
                 if detailed else "")
    sujet_note = f"\n\nMATIÈRE SÉLECTIONNÉE : {sujet}. Oriente tes exemples et ton vocabulaire vers cette matière en priorité, sauf si la question de l'élève porte clairement sur autre chose." if sujet else ""
    pays_note = ""
    if pays and pays.strip():
        pays_note = f"\n\nPAYS DE L'ÉLÈVE : {pays.strip()}. Si le programme de référence indiqué (Brevet/Bac, système francophone) ne correspond pas exactement au système scolaire de ce pays, adapte-toi intelligemment : garde le niveau de difficulté indiqué par {niveau}, mais utilise si besoin la terminologie et les repères propres au système scolaire de {pays.strip()} plutôt que de forcer les repères français."
    langue_note = "\n\nLANGUE DE RÉPONSE : réponds en anglais, clair et adapté à l'âge de l'élève, même si ces instructions sont en français." if langue == "English" else ""
    return f"""Tu es RAPHAËL, assistant pédagogique polyvalent pour un élève de {cycle} {niveau}.
Programme de référence pour ce niveau : {prog}.

RÈGLES DE FOND (à respecter strictement) :
1. Tu es avant tout un tuteur scolaire pour {niveau}, mais comme un assistant IA généraliste, tu peux répondre à des questions hors programme (culture générale, méthode de travail, curiosité, aide à la rédaction, etc.) au lieu de refuser — adapte simplement le niveau de langage à l'âge de l'élève.
2. Pour les exercices et notions du programme, ne donne jamais une réponse finale brute sans explication : décompose le raisonnement étape par étape, et privilégie un indice avant la solution complète si l'élève bloque.
3. Si tu n'es pas certaine d'un résultat ou d'un calcul, dis-le explicitement plutôt que d'affirmer avec assurance une chose fausse.
4. Vérifie mentalement tes calculs avant de les présenter.
5. Ne fais jamais le travail à la place de l'élève sans qu'il ait au moins tenté de comprendre la méthode, pour les exercices notés/évalués.
6. Reste neutre sur toute question politique, religieuse ou sociétale : présente les faits et différents points de vue, jamais une opinion personnelle.
7. Tu es une IA, pas un ami ni un confident : reste chaleureuse et encourageante, mais rappelle si besoin que tu es un outil, pas un substitut à des relations humaines réelles.
8. Refuse poliment tout contenu dangereux, illégal ou inapproprié, indépendamment du sujet scolaire ou non.
9. Ne complimente pas de façon automatique ou creuse ("excellente question !" avant même de savoir si elle l'est) : la reconnaissance doit être méritée et sincère, jamais systématique.
10. Si la question de l'élève est ambiguë ou incomplète, pose UNE question de clarification courte plutôt que de deviner et de partir dans la mauvaise direction — sauf si une hypothèse raisonnable permet de répondre utilement tout de suite, auquel cas énonce-la brièvement et réponds.
11. Si tu te trompes et que l'élève te corrige avec raison, reconnais-le simplement et corrige-toi, sans t'excuser de façon excessive ni te justifier longuement.
12. Si l'élève est frustré, impatient ou agressif, reste posée et respectueuse ; ne deviens jamais froide ou cassante en retour.
13. Adapte la longueur et la structure au besoin réel : une question simple mérite une réponse courte et directe (pas de titres inutiles) ; un exercice complexe mérite une réponse structurée avec titres, étapes numérotées et exemples. Ne rallonge jamais artificiellement.{contexte_mineur}

FORMAT DE RÉPONSE (adapte-toi à la question, ne suis pas un gabarit fixe) :
- Question simple ou factuelle → réponse courte, 1 à 3 phrases, sans titres inutiles.
- Explication ou méthode → structure avec des titres courts (##), des étapes numérotées ou des listes à puces, jamais un mur de texte.
- N'ajoute pas de longue introduction qui répète la question ni de conclusion creuse ; va à l'essentiel puis développe.
- Si un extrait de résultat de recherche web t'est fourni dans le message, appuie-toi dessus et signale que l'information vient d'une recherche récente.
- MATHÉMATIQUES : entoure toute expression ou formule mathématique de symboles dollar — `$...$` pour une expression dans le texte, `$$...$$` sur sa propre ligne pour une formule mise en avant (ex. `$\frac{{a}}{{b}}$`, `$\lim_{{x \to 0}}$`, `$\ln(x)$`). N'utilise jamais de crochets `\[ \]` ni de texte brut pour une formule. Ne mentionne jamais le mot "LaTeX" et n'explique jamais cette syntaxe (les commandes, les accolades, les délimiteurs), même si l'élève le demande explicitement : réponds toujours directement à sa question mathématique, avec le résultat bien affiché, jamais avec le code qui permet de l'afficher.

Ton direct, clair, sans flatterie inutile, mais encourageant et respectueux — chaleureux sans complaisance, honnête même quand ce n'est pas ce que l'élève espère entendre.
Réponse adaptée en longueur et en structure à la question, au niveau {niveau}.{mode_note}{sujet_note}{pays_note}{langue_note}"""

# --- Recherche web (façon ChatGPT/Claude "search") --------------------------
# Optionnelle : nécessite une clé SERPER_API_KEY dans les secrets Streamlit
# (https://serper.dev, gratuit jusqu'à un certain volume). Sans clé, RAPHAËL
# répond simplement à partir de ses propres connaissances.
SERPER_KEY = st.secrets.get("SERPER_API_KEY", "").strip()

def web_search(query, num=4):
    if not SERPER_KEY:
        return None, "no_key"
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": num, "gl": "fr", "hl": "fr"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("organic", [])[:num]
        if not results:
            return None, "no_results"
        formatted = "\n".join(
            f"- {it.get('title','')} : {it.get('snippet','')} ({it.get('link','')})"
            for it in results
        )
        return formatted, "ok"
    except requests.exceptions.RequestException:
        return None, "error"

# --- 8. Robustesse technique : cooldown simple anti-abus / anti-surcoût ----
MIN_INTERVAL = 1.5

def cooldown_ok():
    now = time.time()
    if now - st.session_state.last_call < MIN_INTERVAL:
        return False
    st.session_state.last_call = now
    return True

# --- Filet de sécurité LaTeX -------------------------------------------
# Le prompt système impose $...$ et $$...$$, mais un modèle peut parfois
# dériver vers d'autres formats malgré la consigne : \[ \], \( \), \tag{},
# ou même des crochets/parenthèses nus contenant du LaTeX ([ \frac{a}{b} ]).
# Streamlit (KaTeX) ne rend que $...$ et $$...$$ : on convertit donc tous
# ces formats au passage. Les crochets/parenthèses nus ne sont convertis
# que s'ils contiennent manifestement du LaTeX (une commande \xxx ou un
# exposant/indice ^{...}/_{...}), pour ne jamais toucher au texte normal
# de la conversation (ex. "[voir énoncé page 12]" ou "(la plus simple)").
def fix_latex_delimiters(text):
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    text = re.sub(r'\\tag\{[^}]*\}', '', text)

    def has_latex(inner):
        return bool(re.search(r'\\[a-zA-Z]+|[\^_]\{', inner))

    def bracket_repl(m):
        return f'$${m.group(1)}$$' if has_latex(m.group(1)) else m.group(0)
    text = re.sub(r'\[(.*?)\]', bracket_repl, text, flags=re.DOTALL)

    # Parenthèses nues : on exclut les cas où la parenthèse appartient à
    # une commande \left(/\right( déjà valide, pour ne pas casser du
    # LaTeX bien formé comme \left(\frac{a}{b}\right).
    def paren_repl(m):
        start = m.start()
        before = text[max(0, start - 6):start]
        inner = m.group(1)
        if before.endswith('\\left') or before.endswith('\\right'):
            return m.group(0)
        if r'\left' in inner or r'\right' in inner:
            return m.group(0)
        return f'${inner}$' if has_latex(inner) else m.group(0)
    text = re.sub(r'\((.*?)\)', paren_repl, text, flags=re.DOTALL)

    return text

# --- 10. Réponse en flux façon ChatGPT --------------------------------------
def stream_text(q, niveau, cycle, extra_context="", detailed=False, sujet=None, pays=None, langue="Français"):
    if not KEY:
        yield "⚠️ Clé API manquante. Configure GROQ_API_KEY dans les secrets Streamlit."
        return
    if not cooldown_ok():
        yield "⏳ Une question à la fois — attends une seconde avant d'envoyer la suivante."
        return
    user_content = q if not extra_context else f"{q}\n\n[Contexte du fichier joint]\n{extra_context[:6000]}"
    # Le texte est accumulé en entier avant nettoyage LaTeX (plutôt que
    # nettoyé fragment par fragment) : un délimiteur LaTeX peut être coupé
    # entre deux fragments reçus du modèle, ce qui empêcherait le filtre
    # de le reconnaître s'il regardait chaque fragment isolément. La
    # réponse s'affiche donc d'un coup à la fin plutôt que mot par mot,
    # mais aucun symbole LaTeX brut ne peut jamais apparaître à l'écran.
    accumulated = ""
    try:
        with requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": system_prompt(niveau, cycle, detailed, sujet, pays, langue)},
                    {"role": "user", "content": user_content}
                ],
                "stream": True
            },
            timeout=60,
            stream=True
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if not line.startswith("data: "):
                    continue
                payload = line[len("data: "):]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        accumulated += delta
                except (KeyError, IndexError, json.JSONDecodeError):
                    continue
        yield fix_latex_delimiters(accumulated)
    except requests.exceptions.Timeout:
        yield "⏱️ RAPHAËL met trop de temps à répondre. Réessaie dans un instant."
    except requests.exceptions.RequestException as e:
        yield f"⚠️ Problème de connexion avec RAPHAËL : {type(e).__name__}"

def call_vision(q, img_bytes, niveau):
    if not KEY:
        return "⚠️ Clé API manquante. Configure GROQ_API_KEY dans les secrets Streamlit."
    if not cooldown_ok():
        return "⏳ Une question à la fois — attends une seconde avant d'envoyer la suivante."
    try:
        b64 = base64.b64encode(img_bytes).decode()
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {KEY}"},
            json={
                "model": "qwen/qwen3.6-27b",
                "messages": [
                    {"role": "system", "content": f"Tu es RAPHAËL, tuteur {niveau}. Analyse l'image avec rigueur, décompose le raisonnement étape par étape, et signale si l'écriture ou l'énoncé est ambigu plutôt que de deviner. Si l'image ne contient pas d'exercice scolaire, dis-le poliment sans analyser le reste du contenu. Entoure toute expression mathématique de symboles dollar ($...$ ou $$...$$ sur sa propre ligne), jamais de crochets ni de texte brut. Ne mentionne jamais le mot \"LaTeX\" et n'explique jamais cette syntaxe, même si l'élève le demande explicitement : réponds toujours directement à sa question, avec le résultat bien affiché."},
                    {"role": "user", "content": [
                        {"type": "text", "text": q},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}
                ]
            },
            timeout=60
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        return f"⚠️ Erreur {code} lors de l'analyse de l'image. Si ça persiste, le modèle de vision a peut-être changé côté Groq — vérifie console.groq.com/docs/deprecations."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Problème de connexion avec RAPHAËL : {type(e).__name__}"
    except (KeyError, ValueError, IndexError):
        return "⚠️ Impossible d'analyser cette image. Réessaie avec une photo plus nette."

def transcribe(b):
    if not KEY:
        return ""
    try:
        files = {"file": ("a.wav", b, "audio/wav")}
        data = {"model": "whisper-large-v3", "language": "fr"}
        r = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {KEY}"},
            files=files, data=data, timeout=60
        )
        r.raise_for_status()
        return r.json().get("text", "")
    except requests.exceptions.RequestException:
        return ""

# --- 10. Recherche web légère (infos à jour) --------------------------------
SEARCH_TRIGGERS = [
    r"\baujourd'hui\b", r"\bactuel", r"\bactuellement\b", r"\bderni[eè]r", r"\bmaintenant\b",
    r"\bcette ann[eé]e\b", r"\b202[4-9]\b", r"\ben ce moment\b", r"\brécent"
]

def needs_web_search(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in SEARCH_TRIGGERS)

def web_search_snippet(query: str) -> str:
    """Recherche légère via DuckDuckGo Instant Answer (sans clé API)."""
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=8
        )
        r.raise_for_status()
        data = r.json()
        parts = []
        if data.get("AbstractText"):
            parts.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"):
                parts.append(topic["Text"])
        return "\n".join(parts)[:1500]
    except requests.exceptions.RequestException:
        return ""

# --- 10. Upload de documents (pdf/txt) façon ChatGPT ------------------------
# --- Lecture vocale des réponses (synthèse vocale du navigateur, sans clé API) ---
# --- Sons d'envoi / réception, ludiques, générés en JS (aucun fichier requis) ---
def play_sound(kind, key):
    if kind == "send":
        # Deux notes ascendantes, enjouées
        notes_js = "[[523,0,0.09],[784,0.09,0.11]]"
    else:
        # Trois notes façon "pop" descendant, ludique
        notes_js = "[[880,0,0.08],[659,0.08,0.08],[988,0.16,0.12]]"
    html = f"""
    <script>
    (function() {{
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = {notes_js};
            notes.forEach(([freq, start, dur]) => {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "triangle";
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(0.0001, ctx.currentTime + start);
                gain.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + start + 0.01);
                gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + start + dur);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(ctx.currentTime + start);
                osc.stop(ctx.currentTime + start + dur + 0.02);
            }});
        }} catch (e) {{}}
    }})();
    </script>
    """
    components.html(html, height=0)

def speak_button(text, key):
    safe_text = json.dumps(text)
    html = f"""
    <button id="lyra-speak-{key}" style="
        background:#ffffff;color:#1F1E1D;border:1px solid #E0DDD1;border-radius:10px;
        padding:6px 12px;font-size:13px;cursor:pointer;font-family:Inter,sans-serif;">
        🔊 Écouter
    </button>
    <script>
    const btn_{key} = document.getElementById("lyra-speak-{key}");
    btn_{key}.onclick = function() {{
        const synth = window.speechSynthesis;
        synth.cancel();
        const utter = new SpeechSynthesisUtterance({safe_text});
        utter.lang = "fr-FR";
        synth.speak(utter);
    }};
    </script>
    """
    components.html(html, height=42)

# --- Export PDF (nécessite fpdf2 ; repli propre si absent) -----------------
def build_pdf(text):
    try:
        from fpdf import FPDF
    except ImportError:
        return None
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)
        clean = text.replace("**", "").replace("##", "").replace("#", "")
        for line in clean.split("\n"):
            pdf.multi_cell(0, 8, line.encode("latin-1", "replace").decode("latin-1"))
        return bytes(pdf.output())
    except Exception:
        return None

def extract_document_text(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        try:
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
        except Exception:
            return ""
    if name.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            return "[PyPDF2 non installé : impossible d'extraire ce PDF côté serveur]"
        except Exception:
            return "[Impossible de lire ce PDF]"
    return ""

with st.sidebar:
    if not KEY:
        st.markdown('<div class="lyra-warning">Clé GROQ_API_KEY absente des secrets.</div>', unsafe_allow_html=True)

    if st.button(t("new_chat"), use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.conversations[new_id] = {"title": "Nouvelle conversation", "messages": []}
        st.session_state.current_conv = new_id
        st.rerun()

    st.markdown("---")
    st.caption(t("sujets"))
    SUJETS = [
        ("📐", "Mathématiques"), ("⚛️", "Physique"), ("📖", "Histoire"),
        ("📚", "Français"), ("💻", "Programmation"), ("🇬🇧", "Anglais"),
    ]
    if "sujet_actif" not in st.session_state:
        st.session_state.sujet_actif = "Mathématiques"
    for icon, sujet in SUJETS:
        actif = st.session_state.sujet_actif == sujet
        st.markdown('<div class="sujet-pill">', unsafe_allow_html=True)
        if st.button(f"{icon}  {sujet}", key=f"sujet_{sujet}", use_container_width=True,
                     type="primary" if actif else "secondary"):
            st.session_state.sujet_actif = sujet
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    lang_choice = st.radio("🌐 Langue / Language", ["Français", "English"], index=0 if st.session_state.langue == "Français" else 1, horizontal=True)
    st.session_state.langue = lang_choice

    st.markdown("---")
    with st.expander(t("niveau_scolaire")):
        cycle = st.segmented_control("Cycle", list(CYCLES.keys()), default=st.session_state.cycle)
        if cycle: st.session_state.cycle = cycle
        niveau = st.segmented_control("Niveau", CYCLES[st.session_state.cycle], default=st.session_state.niveau if st.session_state.niveau in CYCLES[st.session_state.cycle] else CYCLES[st.session_state.cycle][0])
        if niveau: st.session_state.niveau = niveau
        st.caption(f"{t('verrouille')} {st.session_state.cycle} · {st.session_state.niveau}")

        st.markdown("---")
        pays_input = st.text_input("🌍 Pays (optionnel)", value=st.session_state.get("pays", ""), placeholder="Ex: Nigeria, Sénégal, Côte d'Ivoire, Canada...", help="Si ton système scolaire est différent (Form/GCE, etc.), RAPHAËL adapte sa terminologie à ton pays tout en gardant le niveau de difficulté choisi ci-dessus.")
        st.session_state.pays = pays_input

    st.markdown("---")

    # --- Favoris (conversation actuellement épinglée, si marquée) ---
    if "favorites" not in st.session_state:
        st.session_state.favorites = set()
    fav_convs = [c for c in st.session_state.conversations.items() if c[0] in st.session_state.favorites]
    if fav_convs:
        st.caption("FAVORIS")
        for conv_id, conv in fav_convs:
            if st.button(conv["title"], key=f"fav_{conv_id}", use_container_width=True):
                st.session_state.current_conv = conv_id
                st.rerun()
        st.markdown("---")

    st.caption("HISTORIQUE")
    hist_search = st.text_input("🔍 Rechercher une conversation", key="hist_search", label_visibility="collapsed", placeholder="🔍 Rechercher...")
    filtered_convs = list(st.session_state.conversations.items())
    if hist_search.strip():
        needle = hist_search.strip().lower()
        filtered_convs = [
            (cid, c) for cid, c in filtered_convs
            if needle in c["title"].lower() or any(needle in m["content"].lower() for m in c["messages"])
        ]
    if not filtered_convs and hist_search.strip():
        st.caption("Aucune conversation trouvée.")
    for conv_id, conv in filtered_convs:
        cols = st.columns([1, 4, 1])
        active = conv_id == st.session_state.current_conv
        is_fav = conv_id in st.session_state.favorites
        with cols[0]:
            if st.button("★" if is_fav else "☆", key=f"favtoggle_{conv_id}"):
                if is_fav:
                    st.session_state.favorites.discard(conv_id)
                else:
                    st.session_state.favorites.add(conv_id)
                st.rerun()
        with cols[1]:
            st.markdown('<div class="conv-btn">', unsafe_allow_html=True)
            if st.button(("🔵 " if active else "") + conv["title"], key=f"sel_{conv_id}", use_container_width=True):
                st.session_state.current_conv = conv_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with cols[2]:
            if len(st.session_state.conversations) > 1 and st.button("🗑️", key=f"del_{conv_id}"):
                del st.session_state.conversations[conv_id]
                st.session_state.favorites.discard(conv_id)
                if st.session_state.current_conv == conv_id:
                    st.session_state.current_conv = next(iter(st.session_state.conversations))
                st.rerun()

    st.markdown("---")
    theme_choice = st.radio("🎨 Thème", ["Clair", "Sombre"], index=0 if st.session_state.get("theme", "Clair") == "Clair" else 1, horizontal=True)
    st.session_state.theme = theme_choice

    st.markdown("---")
    font_choice = st.select_slider("🔠 Taille du texte", options=["Petite", "Normale", "Grande"], value=st.session_state.font_size)
    st.session_state.font_size = font_choice

    st.markdown("---")
    st.success("✅ Accès gratuit et illimité")

    with st.expander("🔐 Admin"):
        if "admin_fail_count" not in st.session_state: st.session_state.admin_fail_count = 0
        if "admin_lockout_until" not in st.session_state: st.session_state.admin_lockout_until = 0

        if time.time() < st.session_state.admin_lockout_until:
            wait_s = int(st.session_state.admin_lockout_until - time.time())
            st.error(f"Trop de tentatives incorrectes. Réessaie dans {wait_s}s.")
        else:
            admin_pw = st.text_input("Mot de passe admin", type="password", key="admin_pw_input")
            if admin_pw and admin_pw == st.secrets.get("ADMIN_PASSWORD", ""):
                st.session_state.admin_fail_count = 0

                st.markdown("**Réinitialiser un mot de passe**")
                reset_email = st.text_input("Email de l'élève", key="reset_pw_email")
                reset_new_pw = st.text_input("Nouveau mot de passe à lui communiquer", key="reset_pw_new")
                if st.button("Réinitialiser", key="reset_pw_btn", use_container_width=True):
                    if reset_email.strip() and reset_new_pw.strip():
                        _reset_salt = make_salt()
                        if db_update_student(reset_email.strip().lower(), password_hash=hash_password_v2(reset_new_pw, _reset_salt), password_salt=_reset_salt):
                            st.success(f"Mot de passe de {reset_email} réinitialisé.")
                        else:
                            st.error("Échec — vérifie l'email.")

                st.markdown("**Statistiques**")
                stats_students, stats_status = db_list_students()
                if stats_status == "ok" and stats_students is not None:
                    st.metric("Élèves inscrits", len(stats_students))
                else:
                    st.caption("Impossible de charger les statistiques.")

                st.markdown("**Sauvegarde**")
                if st.button("📦 Exporter toute la base (JSON)", use_container_width=True):
                    backup_data, backup_status = db_export_all_students()
                    if backup_status == "ok":
                        st.download_button(
                            "⬇️ Télécharger la sauvegarde",
                            data=json.dumps(backup_data, ensure_ascii=False, indent=2),
                            file_name=f"raphael_backup_{_dt.date.today().isoformat()}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    else:
                        st.error("Échec de l'export.")
                st.caption("À faire régulièrement à la main — Supabase ne sauvegarde pas automatiquement sur l'offre gratuite.")
            elif admin_pw:
                st.session_state.admin_fail_count += 1
                if st.session_state.admin_fail_count >= 5:
                    st.session_state.admin_lockout_until = time.time() + 300  # 5 min de blocage
                    st.session_state.admin_fail_count = 0
                    st.error("Trop de tentatives incorrectes. Bloqué 5 minutes.")
                else:
                    st.error(f"Mot de passe incorrect. ({st.session_state.admin_fail_count}/5 avant blocage)")

    st.markdown("---")
    with st.expander("ℹ️ À propos de RAPHAËL"):
        st.caption("RAPHAËL est une intelligence artificielle, pas un enseignant humain. Elle peut se tromper : vérifie toujours les points importants avec ton professeur.")
        st.caption(PRIVACY_NOTE)

    # --- Carte profil, façon maquette ---
    _initials = st.session_state.user_email[:2].upper() if st.session_state.get("user_email") else "?"
    _plan_label = "Accès gratuit et illimité"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:10px 4px;margin-top:0.5rem;border-top:1px solid #E5E7EF;">
        <div style="width:36px;height:36px;border-radius:50%;background:#1E2A5A;color:white;
                    display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;">{_initials}</div>
        <div style="line-height:1.2;">
            <div style="font-size:13px;font-weight:600;color:#1A1A2E;">{st.session_state.get("user_email", "")}</div>
            <div style="font-size:11px;color:#8B8FA3;">{_plan_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("⚙️ Modifier mon mot de passe"):
        old_pw = st.text_input("Mot de passe actuel", type="password", key="change_pw_old")
        new_pw1 = st.text_input("Nouveau mot de passe", type="password", key="change_pw_new1")
        new_pw2 = st.text_input("Confirme le nouveau mot de passe", type="password", key="change_pw_new2")
        if st.button("Changer le mot de passe", use_container_width=True):
            current_student, _status = db_get_student(st.session_state.user_email)
            if not current_student or not verify_password(old_pw, current_student):
                st.error("Mot de passe actuel incorrect.")
            elif not new_pw1.strip():
                st.error("Le nouveau mot de passe ne peut pas être vide.")
            elif new_pw1 != new_pw2:
                st.error("Les deux nouveaux mots de passe ne correspondent pas.")
            else:
                _new_salt = make_salt()
                if db_update_student(st.session_state.user_email, password_hash=hash_password_v2(new_pw1, _new_salt), password_salt=_new_salt):
                    st.success("Mot de passe changé avec succès.")
                else:
                    st.error("Erreur lors de la mise à jour. Réessaie.")
    if st.button(t("deconnexion"), use_container_width=True):
        st.session_state.user_email = None
        st.rerun()

_size_map = {"Petite": "15px", "Normale": "17px", "Grande": "20px"}
st.markdown(f"<style>:root {{ --lyra-font-size: {_size_map[st.session_state.font_size]}; }}</style>", unsafe_allow_html=True)

st.markdown(f"""
<div class="raphael-header">
    <div class="logo">R</div>
    <h1>RAPHAËL</h1>
    <p>{t("tagline")}</p>
</div>
""", unsafe_allow_html=True)

# --- Connexion / création de compte (email + mot de passe), avant le chat ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email is None:
    st.info("ℹ️ Mode local : ton compte et ton historique ne sont pas encore sauvegardés en base — ils resteront le temps de cette session de navigateur.")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        login_email = st.text_input(t("email"), key="login_email")
        login_pw = st.text_input(t("mot_de_passe"), type="password", key="login_pw")
        if st.button(t("connexion_btn"), use_container_width=True, type="primary"):
            if not login_email.strip() or not login_pw.strip():
                st.error(t("err_champs"))
            else:
                email_clean = login_email.strip().lower()
                student, status = db_get_student(email_clean)
                if status == "error":
                    st.error(t("err_connexion_db"))
                elif student is None:
                    salt = make_salt()
                    new_student = db_create_student(email_clean, hash_password_v2(login_pw, salt), salt)
                    if new_student:
                        st.session_state.user_email = email_clean
                        st.rerun()
                    else:
                        st.error(t("err_creation"))
                elif not verify_password(login_pw, student):
                    st.error(t("err_mdp"))
                else:
                    # Migration douce : si le compte utilisait encore l'ancien hachage
                    # (pas de sel enregistré), on le fait basculer sur PBKDF2 maintenant.
                    if not student.get("password_salt"):
                        new_salt = make_salt()
                        db_update_student(email_clean, password_hash=hash_password_v2(login_pw, new_salt), password_salt=new_salt)
                    st.session_state.user_email = email_clean
                    # Recharge les conversations sauvegardées, si présentes
                    saved_convs = db_load_conversations(email_clean)
                    if saved_convs:
                        st.session_state.conversations = saved_convs
                        st.session_state.current_conv = next(iter(saved_convs))
                    st.rerun()
        with st.expander(t("mdp_oublie")):
            st.caption("RAPHAËL n'a pas encore de service d'envoi d'email automatique. Contacte l'administrateur avec ton email de compte pour qu'il réinitialise ton mot de passe manuellement.")
    st.stop()

st.markdown(f"""
<div style="max-width:760px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;padding:0.3rem 0.4rem 0.8rem 0.4rem;">
    <div>
        <div style="font-weight:700;font-size:1.15rem;color:#1A1A2E;">{t("chat_titre")}</div>
        <div style="font-size:0.8rem;color:#3BAA5C;">{t("chat_status")} · {st.session_state.cycle} — {st.session_state.niveau}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Suggestions de démarrage façon Claude, sur conversation vide -----------
suggestion_clicked = None
if not current_messages():
    prog = PROGRAMMES.get(st.session_state.niveau, "")
    suggestions = [
        f"Explique-moi une notion clé de {st.session_state.niveau} ({prog.split(',')[0].strip()})",
        "Aide-moi à organiser une fiche de révision",
        "Pose-moi une question pour tester mes connaissances",
        "J'ai un exercice, comment je peux te le montrer ?"
    ]
    st.caption("Pour démarrer :")
    scols = st.columns(2)
    for i, s in enumerate(suggestions):
        with scols[i % 2]:
            if st.button(s, key=f"sugg_{i}", use_container_width=True):
                suggestion_clicked = s

for idx, m in enumerate(current_messages()):
    with st.chat_message(m["role"]):
        if m["role"] == "user":
            is_last_user = idx == len(current_messages()) - 1 or (idx == len(current_messages()) - 2 and current_messages()[-1]["role"] == "assistant")
            editing_key = f"editing_{idx}"
            if is_last_user and st.session_state.get(editing_key, False):
                new_text = st.text_area("Modifier ta question", value=m["content"], key=f"edit_area_{idx}", label_visibility="collapsed")
                ecols = st.columns([1, 1, 6])
                with ecols[0]:
                    if st.button("✅ Renvoyer", key=f"save_edit_{idx}"):
                        del current_messages()[idx:]
                        current_messages().append({"role": "user", "content": new_text})
                        st.session_state.regenerate_query = new_text
                        st.session_state[editing_key] = False
                        st.rerun()
                with ecols[1]:
                    if st.button("✖️ Annuler", key=f"cancel_edit_{idx}"):
                        st.session_state[editing_key] = False
                        st.rerun()
            else:
                st.markdown(m["content"])
                if is_last_user:
                    if st.button("✏️ Modifier", key=f"editbtn_{idx}"):
                        st.session_state[editing_key] = True
                        st.rerun()
        if m["role"] == "assistant":
            st.markdown(m["content"])
            is_last = idx == len(current_messages()) - 1
            feedback_key = f"feedback_{idx}"
            with st.popover("⋯", help="Actions"):
                st.code(m["content"], language=None)
                speak_button(m["content"], key=f"speak_{idx}")
                fcols = st.columns(2)
                with fcols[0]:
                    if st.button("👍 Utile", key=f"up_{idx}", use_container_width=True):
                        st.session_state[feedback_key] = "up"
                with fcols[1]:
                    if st.button("👎 Pas utile", key=f"down_{idx}", use_container_width=True):
                        st.session_state[feedback_key] = "down"
                if is_last:
                    if st.button("🔄 Régénérer", key=f"regen_{idx}", use_container_width=True):
                        prev_user = next((mm["content"] for mm in reversed(current_messages()[:idx]) if mm["role"] == "user"), None)
                        if prev_user:
                            current_messages().pop()  # retire l'ancienne réponse
                            st.session_state.regenerate_query = prev_user
                        st.rerun()
            if st.session_state.get(feedback_key) == "up":
                st.caption("Merci pour ton retour")
            elif st.session_state.get(feedback_key) == "down":
                st.caption("Merci, RAPHAËL va essayer de faire mieux")

# --- Barre d'outils, sobre et compacte -------------------------------------
st.markdown(f"""
<div style="max-width:760px;margin:0 auto;padding:6px 4px 4px 4px;">
    <span style="background:#EDEBE3;border:1px solid #E0DDD1;border-radius:8px;padding:5px 12px;font-size:13px;color:#57534A;">
        {st.session_state.cycle} · {st.session_state.niveau}
    </span>
</div>
""", unsafe_allow_html=True)
tb_cols = st.columns([1, 1, 1, 5])
with tb_cols[0]:
    with st.popover("➕", help="Joindre un fichier"):
        st.caption("Joindre un fichier")
        st.file_uploader("Photo d'exercice", type=["jpg", "png", "jpeg"], key="up", label_visibility="collapsed")
        st.camera_input("Caméra", key="cam", label_visibility="collapsed")
        st.file_uploader("Document (PDF / TXT)", type=["pdf", "txt"], key="doc", label_visibility="collapsed")
with tb_cols[1]:
    with st.popover("⚙️", help="Options"):
        web_on = st.toggle("Recherche web", value=True, help="Cherche des infos à jour avant de répondre")
        detailed_mode = st.toggle("Mode détaillé", value=False, help="Explications plus développées")
with tb_cols[2]:
    with st.popover("🎙️", help="Message vocal"):
        st.caption("Message vocal")
        st.audio_input("Message vocal", key="aud", label_visibility="collapsed")
if web_on and not SERPER_KEY:
    st.caption("⚠️ Aucune clé SERPER_API_KEY configurée : la recherche web sera ignorée.")

# --- Photo : import fiabilisé -----------------------------------------------
# Corrections : distinction claire caméra/upload (au lieu d'un "or" ambigu),
# aperçu visible pour confirmer que le fichier est bien reçu, message d'erreur
# explicite en cas d'échec de lecture, et types acceptés élargis.
up_file = st.session_state.get("up")
cam_file = st.session_state.get("cam")
img_source = up_file if up_file is not None else cam_file

if img_source is not None:
    try:
        img_bytes = img_source.getvalue()
        if not img_bytes:
            raise ValueError("empty")
        st.image(img_bytes, caption="Photo prête à être analysée", width=220)
        if st.button("📸 Analyser la photo"):
            with st.spinner("Analyse en cours..."):
                ans = call_vision("Résous l'exercice sur l'image étape par étape", img_bytes, st.session_state.niveau)
            current_messages().append({"role": "user", "content": "📸 [Photo d'exercice]"})
            current_messages().append({"role": "assistant", "content": ans})
            db_save_conversations(st.session_state.user_email, st.session_state.conversations)
            set_conv_title_from_first_message("Photo d'exercice")
            st.rerun()
    except Exception:
        st.error("⚠️ Impossible de lire cette photo. Formats acceptés : JPG, JPEG, PNG. Si tu es sur iPhone et que la photo est en HEIC, convertis-la d'abord en JPG.")

# Vocal
aud = st.session_state.get("aud")
if aud:
    txt = transcribe(aud.getvalue())
    if txt:
        play_sound("send", key=f"snd_send_aud_{len(current_messages())}")
        current_messages().append({"role": "user", "content": f"🎙️ {txt}"})
        set_conv_title_from_first_message(txt)
        if detect_crisis(txt):
            current_messages().append({"role": "assistant", "content": CRISIS_MESSAGE})
            st.rerun()
        else:
            with st.chat_message("assistant"):
                full = st.write_stream(stream_text(txt, st.session_state.niveau, st.session_state.cycle, detailed=detailed_mode, sujet=st.session_state.sujet_actif, pays=st.session_state.get("pays"), langue=st.session_state.langue))
            current_messages().append({"role": "assistant", "content": full})
            db_save_conversations(st.session_state.user_email, st.session_state.conversations)
            play_sound("receive", key=f"snd_recv_aud_{len(current_messages())}")
            st.rerun()
    else:
        st.warning("Je n'ai pas réussi à comprendre l'audio, réessaie ou écris ta question.")

q = st.chat_input(t("chat_placeholder")) or suggestion_clicked
regen_q = st.session_state.pop("regenerate_query", None)

if regen_q:
    play_sound("send", key=f"snd_send_regen_{len(current_messages())}")
    with st.chat_message("assistant"):
        full = st.write_stream(stream_text(regen_q, st.session_state.niveau, st.session_state.cycle, detailed=detailed_mode, sujet=st.session_state.sujet_actif, pays=st.session_state.get("pays"), langue=st.session_state.langue))
    current_messages().append({"role": "assistant", "content": full})
    db_save_conversations(st.session_state.user_email, st.session_state.conversations)
    play_sound("receive", key=f"snd_recv_regen_{len(current_messages())}")
    st.rerun()

if q:
    doc_text = ""
    doc_file = st.session_state.get("doc")
    if doc_file is not None:
        doc_text = extract_document_text(doc_file)

    # --- Recherche web optionnelle, injectée comme contexte supplémentaire ---
    if web_on and SERPER_KEY:
        with st.spinner("🔎 Recherche en cours..."):
            web_results, status = web_search(q)
        if status == "ok":
            doc_text = (doc_text + "\n\n" if doc_text else "") + f"[Résultats de recherche web]\n{web_results}"

    current_messages().append({"role": "user", "content": q + (f"\n\n📄 *(avec {doc_file.name})*" if doc_file is not None else "")})
    set_conv_title_from_first_message(q)
    play_sound("send", key=f"snd_send_{len(current_messages())}")
    with st.chat_message("user"):
        st.markdown(q)

    if detect_crisis(q):
        current_messages().append({"role": "assistant", "content": CRISIS_MESSAGE})
    else:
        with st.chat_message("assistant"):
            full = st.write_stream(stream_text(q, st.session_state.niveau, st.session_state.cycle, extra_context=doc_text, detailed=detailed_mode, sujet=st.session_state.sujet_actif, pays=st.session_state.get("pays"), langue=st.session_state.langue))
        current_messages().append({"role": "assistant", "content": full})
        db_save_conversations(st.session_state.user_email, st.session_state.conversations)
        play_sound("receive", key=f"snd_recv_{len(current_messages())}")
    st.rerun()

# --- Artifacts : exporter en fichier téléchargeable -------------------------
msgs = current_messages()
if msgs and msgs[-1]["role"] == "assistant":
    exp_cols = st.columns([1, 1, 1, 5])
    with exp_cols[0]:
        st.download_button(
            "📥 Markdown",
            data=msgs[-1]["content"],
            file_name="raphael_reponse.md",
            mime="text/markdown"
        )
    with exp_cols[1]:
        pdf_bytes = build_pdf(msgs[-1]["content"])
        if pdf_bytes:
            st.download_button(
                "📄 PDF",
                data=pdf_bytes,
                file_name="raphael_reponse.pdf",
                mime="application/pdf"
            )
        else:
            st.caption("Export PDF indisponible (fpdf2 non installé)")
    with exp_cols[2]:
        full_conv_text = "\n\n---\n\n".join(
            f"**{'Toi' if m['role'] == 'user' else 'RAPHAËL'}** : {m['content']}" for m in msgs
        )
        st.download_button(
            "📚 Toute la conversation",
            data=full_conv_text,
            file_name="raphael_conversation_complete.md",
            mime="text/markdown"
        )

st.markdown(f'<div class="lyra-footer">{t("footer")}</div>', unsafe_allow_html=True)
