# =============================================
# 1. IMPORTS ET CONFIGURATION INITIALE
# =============================================
# Import des bibliothèques nécessaires :
# - nicegui pour l'interface web
# - sql_manager (module personnalisé) pour gérer la base de données
# - css (module personnalisé) pour les styles
# - os pour gérer les variables d'environnement
# - sqlite3 pour interagir directement avec la base SQLite
from nicegui import app, ui
import sql_manager as db
import css
import os
import sqlite3

# Configuration des fichiers statiques (images, PDF, etc.)
# Le dossier '/static' dans l'application web pointe vers le dossier 'static' local
app.add_static_files('/static', 'static')

# =============================================
# 2. CLASSE AppState : GESTION DE L'ÉTAT UTILISATEUR
# =============================================
# Cette classe stocke l'état de l'application pour chaque utilisateur.
# Elle permet de conserver les choix de l'utilisateur entre les rafraîchissements de l'UI.
class AppState:
    def __init__(self):
        self.step = 0                # Étape actuelle dans le flux de navigation (0 = splash screen)
        self.lang = 'FR'             # Langue actuelle (FR ou EN)
        self.choix = {}              # Dictionnaire stockant les choix de l'utilisateur (métier, thème, etc.)
        self.code_metier_affiche = "" # Texte affiché pour le métier sélectionné (ex: "Socle Assistant Maternel")
        self.art_cible = ""          # Numéro de l'article ciblé (pour la recherche directe)
        self.annexe_selectionnee = None # Numéro de l'annexe sélectionnée

# =============================================
# 3. FONCTION render_result : AFFICHAGE D'UN ARTICLE
# =============================================

import re

def render_result(num_article, txt, current_state):
    if not num_article or num_article == "None":
        ui.label("⚠️ Article non renseigné").classes('text-orange-500 p-4 bg-orange-50 rounded-xl w-full')
        return

    container_lies = ui.column().classes('w-full mt-4')

    def charger_article_cité(n_art):
        with container_lies:
            ui.separator().classes('my-4 border-dashed border-blue-300')
            render_result(n_art, txt, current_state)

    articles = db.fetch_articles_complet(num_article)
    ui.label(f"Article {num_article}").classes('text-xl font-bold text-blue-700 w-full mb-4')

    for art in articles:
        with ui.column().classes('article-card w-full border-l-4 border-blue-200 pl-4 mb-6'):
            ui.label(art['affichage_article']).classes('font-bold text-lg text-slate-900')

            res_col = 'texte_simplifie' if current_state.lang == 'FR' else 'texte_simplifie_en'
            if art[res_col]:
                with ui.column().classes('bg-blue-50 p-4 rounded-xl w-full my-3 border border-blue-100'):
                    ui.label(art[res_col]).classes('text-slate-800')

            with ui.expansion(txt.get('official', '⚖️ Texte officiel')).classes('w-full text-sm text-slate-500 border-t mt-4'):
                ui.markdown(art['texte_integral']).classes('text-[12px] italic')
                
                # --- NOUVELLE LOGIQUE DE DÉTECTION PRÉCISE ---
                # On cherche "article" précédé optionnellement de l' ou l’
                # \b assure qu'on ne prend pas un mot contenant "article" au milieu
                # \s+ gère un ou plusieurs espaces
                regex_article = r"(?:l['’])?article\s+(\d+)"
                matches = re.findall(regex_article, art['texte_integral'], re.IGNORECASE)
                
                if matches:
                    # On retire les doublons et le numéro de l'article actuel
                    articles_cites = list(set([m for m in matches if str(m) != str(num_article)]))
                    
                    for num_cite in articles_cites:
                        ui.button(f"📄 Consulter l'article {num_cite} cité", 
                                  on_click=lambda n=num_cite: charger_article_cité(n)) \
                            .props('flat color=primary icon=launch') \
                            .classes('mt-4 font-bold bg-blue-50 w-full text-left')

    container_lies.move(ui.get_context().parent)
    
# =============================================
# 4. FONCTION build_ui : MOTEUR PRINCIPAL DE L'INTERFACE
# =============================================
# Cette fonction génère dynamiquement l'interface utilisateur en fonction de l'état actuel.
# Elle est décorée avec @ui.refreshable pour permettre les mises à jour sans rechargement de page.
@ui.refreshable
def build_ui(state, h_zone, c_zone):
    # Efface le contenu des zones d'en-tête et de contenu à chaque rafraîchissement
    h_zone.clear()
    c_zone.clear()

    # =============================================
    # 4.1. FONCTION INTERNE set_step : CHANGEMENT D'ÉTAPE
    # =============================================
    # Met à jour l'étape actuelle et les choix de l'utilisateur, puis rafraîchit l'UI.
    def set_step(s, data=None):
        state.step = s
        if data:
            state.choix.update(data)
            # Mapping des codes métier vers des libellés lisibles
            if 'colonne_metier' in data:
                mapping = {
                    "art_am": "Socle Assistant Maternel",
                    "art_sc": "Socle Commun",
                    "art_ef": "Salarié Particulier Employeur"
                }
                state.code_metier_affiche = mapping.get(data['colonne_metier'], "CCN 3239")
            if 'art_cible' in data: state.art_cible = data['art_cible']
            if 'annexe_id' in data: state.annexe_selectionnee = data['annexe_id']
        build_ui.refresh()  # Rafraîchit l'interface

    # Récupère la colonne de filtrage en fonction du métier sélectionné (par défaut : 'art_sc')
    col_filtre = state.choix.get('colonne_metier', 'art_sc')

    # =============================================
    # 4.2. TEXTES DE L'INTERFACE (FR/EN)
    # =============================================
    # Dictionnaire des textes affichés dans l'UI, organisés par langue
    UI_TEXT = {
        'FR': {
            'home': '🏠 ACCUEIL', 'search_label': '🔍 Recherche directe (Ex: 139)', 'search_btn': 'Aller',
            'step1_title': 'Quel est votre métier ?', 'step2_title': 'Quelle est votre situation ?',
            'gestion': 'LA GESTION DU CONTRAT', 'fin': 'LA FIN DU CONTRAT',
            'annexes_btn': '📚 ANNEXES (Résumés & PDF)', 'back': '⬅️ RETOUR',
            'official_pdf': '📄 Consulter le PDF Officiel', 'official': '⚖️ Texte officiel'
        },
        'EN': {
            'home': '🏠 HOME', 'search_label': '🔍 Direct search (Ex: 139)', 'search_btn': 'Go',
            'step1_title': 'What is your job ?', 'step2_title': 'What is your situation ?',
            'gestion': 'CONTRACT MANAGEMENT', 'fin': 'END OF CONTRACT',
            'annexes_btn': '📚 ANNEXES (Summary & PDF)', 'back': '⬅️ BACK',
            'official_pdf': '📄 View Official PDF', 'official': '⚖️ Official text'
        }
    }
    txt = UI_TEXT[state.lang]  # Sélectionne les textes selon la langue actuelle

    # =============================================
    # 4.3. ZONE D'EN-TÊTE (STICKY)
    # =============================================
    with h_zone:
        if state.step != 0:  # Pas d'en-tête sur le splash screen
            with ui.row().classes('w-full px-4 py-3 header-row'):
                # Affiche le métier ou socle sélectionné
                ui.label(state.code_metier_affiche if state.code_metier_affiche else 'CCN 3239') \
                    .classes('text-blue-600 font-black text-base truncate flex-shrink')
                # Boutons de changement de langue
                with ui.row().classes('gap-3 flex-nowrap items-center flex-none'):
                    ui.button('🇫🇷', on_click=lambda: (setattr(state, 'lang', 'FR'), build_ui.refresh())).props('flat').classes('text-xl p-0')
                    ui.button('🇬🇧', on_click=lambda: (setattr(state, 'lang', 'EN'), build_ui.refresh())).props('flat').classes('text-xl p-0')

    # =============================================
    # 4.4. ZONE DE CONTENU (DYNAMIQUE)
    # =============================================
    with c_zone:

        # =============================================
        # ÉTAPE 0 : SPLASH SCREEN (ÉCRAN D'ACCUEIL)
        # =============================================
        if state.step == 0:
            with ui.column().classes('w-full items-center justify-start no-wrap h-screen -mt-[95px] p-0 bg-white'):
                with ui.button(on_click=lambda: set_step(1)).props('flat') \
                    .classes('p-0 m-0 rounded-b-3xl overflow-hidden shadow-xl w-full max-w-[420px] h-[85vh]'):
                    ui.image('/static/accueil.jpg').classes('w-full h-full object-cover object-top')
            return  # On quitte la fonction pour éviter d'afficher d'autres éléments

        # =============================================
        # BOUTON ACCUEIL (AFFICHÉ SAUF SUR SPLASH SCREEN ET ÉTAPE 1)
        # =============================================
        if state.step not in [0, 1]:
            ui.button(txt['home'], on_click=lambda: set_step(1)) \
                .props('flat dense icon=home color=primary') \
                .classes('w-full mb-4 text-slate-500 border-b pb-2')

        # =============================================
        # ÉTAPE 1 : SÉLECTION DU MÉTIER
        # =============================================
        if state.step == 1:
            # Boîte de dialogue pour la recherche directe
            with ui.dialog() as direct_dialog, ui.card().classes('items-center'):
                ui.label(txt['search_label']).classes('font-bold')
                i_direct = ui.input(placeholder="Ex: 139").classes('w-full')
                with ui.row():
                    ui.button(txt['search_btn'], on_click=lambda: (set_step('DIRECT', {'art_cible': i_direct.value}), direct_dialog.close()))
                    ui.button('Fermer', on_click=direct_dialog.close).props('flat')

            # Grille des métiers
            with ui.column().classes('w-full items-center'):
                # Données des métiers : code, libellé FR/EN, icône FontAwesome
                METIERS_DATA = [
                    {"c": "art_am", "fr": "Assistant Maternel", "en": "Childminder", "icon": "fa-baby-carriage"},
                    {"c": "art_ef", "fr": "Assistant Parental", "en": "Nanny", "icon": "fa-baby"},
                    {"c": "art_ef", "fr": "Employé Familial", "en": "Family Employee", "icon": "fa-house-user"},
                    {"c": "art_ef", "fr": "Assistant de Vie", "en": "Life Assistant", "icon": "fa-wheelchair"},
                    {"c": "art_sc", "fr": "Autres métiers CESU", "en": "Other jobs (CESU)", "icon": "fa-briefcase"},
                    {"c": "DIRECT", "fr": "Article CCN 3239 en 1 clic", "en": "Direct Access", "icon": "fa-book-open", "is_direct": True}
                ]

                ui.label(txt['step1_title']).classes('text-xl font-bold text-slate-800 w-full mb-2 px-2')

                # Affichage des cartes de métiers sous forme de grille
                with ui.element('div').classes('grid-container w-full'):
                    for m in METIERS_DATA:
                        label_affiche = m['fr'] if state.lang == 'FR' else m['en']
                        is_special = m.get('is_direct', False)
                        border_color = 'border-[#10b981]' if is_special else 'border-slate-200'

                        # Détermine l'action au clic
                        if is_special:
                            on_click_action = direct_dialog.open  # Ouvre la boîte de dialogue pour la recherche directe
                        else:
                            # Crée une fonction de rappel pour capturer les valeurs actuelles de m
                            def create_click(m_code=m['c'], m_label=label_affiche):
                                return lambda: set_step(2, {'colonne_metier': m_code, 'label_metier': m_label})
                            on_click_action = create_click()

                        # Crée la carte du métier
                        card = ui.card().classes(f'w-full bg-white p-4 border-2 {border_color} shadow-sm cursor-pointer active:opacity-50')
                        card.on('click', on_click_action)

                        with card:
                            with ui.column().classes('items-center justify-center w-full gap-1 pointer-events-none'):
                                if not is_special:
                                    ui.html(f'<i class="fa-solid {m["icon"]} text-black"></i>')
                                    ui.label(label_affiche).classes('font-bold text-center text-slate-800 uppercase leading-tight')
                                else:
                                    ui.html(f'<i class="fa-solid {m["icon"]} text-[#10b981]"></i>')
                                    ui.label("ARTICLE CCN\n3239\nEN 1 CLIC").classes('special-label text-center text-slate-800 leading-tight').style('white-space: pre-line;')

                # Bouton pour accéder aux annexes
                ui.separator().classes('my-2 w-11/12')
                ui.button(txt['annexes_btn'], on_click=lambda: set_step('LISTE_ANNEXES')) \
                    .classes('w-full py-4 animate-entrance shadow-lg text-sm rounded-2xl')

        # =============================================
        # ÉTAPE 2 : SÉLECTION DE LA SITUATION (GESTION/FIN DU CONTRAT)
        # =============================================
        elif state.step == 2:
            ui.label(txt['step2_title']).classes('text-lg font-bold text-slate-700 w-full mb-2 px-2')
            # Filtre pour ne récupérer que les étapes de vie pertinentes pour le métier sélectionné
            f = f"WHERE {col_filtre} IS NOT NULL AND {col_filtre} != ''"
            options = db.fetch_options("etape_vie", state.lang, f)
            with ui.column().classes('w-full'):
                for o in options:
                    # Détermine si c'est une option de "Gestion" ou "Fin" du contrat
                    label_bouton = txt['gestion'] if ("Vie" in o or "Life" in o) else txt['fin']
                    ui.button(label_bouton, on_click=lambda o=o: set_step(3, {'etape_val': o})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(1)).props('flat').classes('w-full mt-4')

        # =============================================
        # ÉTAPE 3 : SÉLECTION DE LA FAMILLE
        # =============================================
        elif state.step == 3:
            # Filtre pour ne récupérer que les familles pertinentes pour l'étape de vie sélectionnée
            f = f"WHERE (etape_vie = '{state.choix['etape_val']}' OR etape_vie_en = '{state.choix['etape_val']}') AND {col_filtre} != ''"
            fams = db.fetch_options("famille", state.lang, f)
            with ui.column().classes('w-full'):
                for f_v in fams:
                    ui.button(f_v, on_click=lambda f_v=f_v: set_step(4, {'famille_val': f_v})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(2)).props('flat').classes('w-full mt-4')

        # =============================================
        # ÉTAPE 4 : SÉLECTION DU THÈME
        # =============================================
        elif state.step == 4:
            # Filtre pour ne récupérer que les thèmes pertinents pour la famille sélectionnée
            f = f"WHERE (famille = '{state.choix['famille_val']}' OR famille_en = '{state.choix['famille_val']}') AND {col_filtre} != ''"
            thms = db.fetch_options("theme", state.lang, f)
            with ui.column().classes('w-full'):
                for t in thms:
                    ui.button(t, on_click=lambda t=t: set_step(5, {'theme': t})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(3)).props('flat').classes('w-full mt-4')

        # =============================================
        # ÉTAPE 5 : SÉLECTION DE LA QUESTION
        # =============================================
        elif state.step == 5:
            # Détermine les colonnes à interroger selon la langue
            col_q = "question_claire" if state.lang == 'FR' else "question_en"
            col_th = "theme" if state.lang == 'FR' else "theme_en"

            # Récupère les questions depuis la base de données
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, {col_q} FROM questions WHERE {col_th} = ? AND {col_filtre} != ''", (state.choix['theme'],))
            questions = cursor.fetchall()
            conn.close()

            # Affiche chaque question sous forme de bouton
            for q in questions:
                ui.button(q[1], on_click=lambda q_id=q[0]: set_step(6, {'id_question': q_id})).classes('w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-left mb-3 font-medium')
            ui.button(txt['back'], on_click=lambda: set_step(4)).props('flat').classes('w-full mt-4')

        # =============================================
        # ÉTAPE 6 : AFFICHAGE DU RÉSULTAT (ARTICLE)
        # =============================================
        elif state.step == 6:
            # Récupère le numéro de l'article associé à la question sélectionnée
            num_art = db.get_article_from_question(state.choix['id_question'], state.choix['colonne_metier'])
            render_result(num_art, txt, state)  # Affiche l'article
            ui.button(txt['back'], on_click=lambda: set_step(5)).props('flat').classes('w-full mt-4')

        # =============================================
        # RECHERCHE DIRECTE : AFFICHAGE DE L'ARTICLE CIBLÉ
        # =============================================
        elif state.step == 'DIRECT':
            render_result(state.art_cible, txt, state)
            ui.button(txt['back'], on_click=lambda: set_step(1)).props('flat').classes('w-full mt-4')

        # =============================================
        # LISTE DES ANNEXES
        # =============================================
        elif state.step == 'LISTE_ANNEXES':
            ui.label(txt['annexes_btn']).classes('text-xl font-bold mb-1')
            ui.label('Documents au 31/12/2024').classes('text-xs text-red-600 font-bold mb-4 italic uppercase border-l-2 border-red-600 px-2')

            # Récupère la liste des annexes depuis la base de données
            conn = sqlite3.connect('CCN_3239.db', timeout=20)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT numero, titre FROM annexes ORDER BY CAST(numero AS INTEGER)").fetchall()
            conn.close()

            # Affiche chaque annexe sous forme de carte cliquable
            with ui.element('div').classes('grid-container w-full'):
                for row in rows:
                    n, t = row['numero'], row['titre']
                    with ui.card().classes('w-full h-28 bg-white text-black border-2 border-slate-300 rounded-2xl shadow-md p-0 overflow-hidden') \
                        .on('click', lambda n=n: set_step('VOIR_ANNEXE', {'annexe_id': n})):
                        with ui.column().classes('items-center justify-center p-3 gap-1 w-full text-center h-full'):
                            ui.label(f"ANNEXE N°{n}").classes('text-[10px] font-black text-blue-600 uppercase')
                            ui.label(t.upper()).classes('text-[10px] font-bold leading-tight text-slate-700 uppercase')

        # =============================================
        # AFFICHAGE D'UNE ANNEXE
        # =============================================
        elif state.step == 'VOIR_ANNEXE':
            # Récupère les données de l'annexe sélectionnée
            conn = sqlite3.connect('CCN_3239.db', timeout=20)
            conn.row_factory = sqlite3.Row
            res = conn.execute("SELECT titre, resume_fr, resume_en, numero FROM annexes WHERE numero = ?", (state.annexe_selectionnee,)).fetchone()
            conn.close()

            if res:
                resume = res['resume_fr'] if state.lang == 'FR' else res['resume_en']

                with ui.column().classes('annexe-container'):
                    # Section titre
                    with ui.element('div').classes('annexe-title-section'):
                        ui.label(f"ANNEXE N°{res['numero']}").classes('text-blue-600 font-bold uppercase text-xs tracking-widest')
                        ui.label(res['titre']).classes('text-2xl font-black text-slate-800 leading-tight')

                    # Section résumé
                    with ui.element('div').classes('annexe-card-info'):
                        ui.markdown(resume if resume else "Résumé à venir...").classes('text-slate-700 leading-relaxed')

                    # Section téléchargement du PDF
                    with ui.card().classes('w-full bg-red-50 p-4 border border-red-100 rounded-2xl items-center mt-4'):
                        ui.label(txt['official_pdf']).classes('text-red-900 font-bold mb-2')
                        pdf_url = f"/static/Annexe_{res['numero']}.pdf"
                        ui.button("TÉLÉCHARGER LE PDF", icon='download', on_click=lambda: ui.download(pdf_url)) \
                            .props('elevated color=red-800').classes('rounded-full')

                    # Bouton retour
                    ui.button(txt['back'], on_click=lambda: set_step('LISTE_ANNEXES')) \
                        .props('flat icon=arrow_back').classes('w-full text-slate-400 mt-4')

# =============================================
# 5. PAGE PRINCIPALE : / (POINT D'ENTRÉE DE L'APPLICATION)
# =============================================
@ui.page('/')
def main_page():
    # Ajoute les balises HTML pour le viewport, FontAwesome et le CSS personnalisé
    ui.add_head_html(f'''
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>{css.STYLE_CSS}</style>
    ''')

    # Initialise l'état utilisateur et les zones d'interface
    user_state = AppState()
    h_zone = ui.column().classes('w-full sticky-header')  # Zone d'en-tête (sticky)
    c_zone = ui.column().classes('w-full max-w-md mx-auto p-4 gap-2 items-center mt-[44px]')  # Zone de contenu
    build_ui(user_state, h_zone, c_zone)  # Lance la construction de l'UI

# =============================================
# 6. LANCEMENT DU SERVEUR NICEGUI
# =============================================
# Configure et lance le serveur web.
# - title : Titre de l'onglet du navigateur
# - host : Accessible depuis toutes les adresses IP (0.0.0.0)
# - port : Port défini par la variable d'environnement PORT (9000 par défaut)
# - reload : Désactive le rechargement automatique (pour la production)
# - reconnect_timeout : Tolérance aux coupures réseau (30 secondes)
# - show : N'affiche pas le message de lancement dans la console
ui.run(
    title="Guide CCN",
    host='0.0.0.0',
    port=int(os.environ.get("PORT", 9000)),
    reload=False,
    reconnect_timeout=30,
    show=False
)
