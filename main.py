# --- 1. IMPORTATIONS DES DÉPENDANCES ---
from nicegui import app, ui
import sql_manager as db
import css
import os
import sqlite3
import random  # <-- Il faut s'assurer qu'il est bien ici
import game_definitions
import game_translation


import os
try:
    os.system("lsof -t -i:9000 | xargs kill -9 > /dev/null 2>&1")
except:
    pass

# --- 2. CONFIGURATION DES RESSOURCES ---
app.add_static_files('/static', 'static')
# 👇 AJOUTEZ CE BLOC ICI POUR SUPPRIMER LES CACHES AGRESSIFS DE SAFARI / IPHONE
@app.middleware
async def add_cache_control_headers(request, call_next):
    response = await call_next(request)
    
    # Si la requête concerne la page d'accueil ou du code HTML
    if request.url.path == "/" or "text/html" in response.headers.get("content-type", ""):
        # Dit au navigateur de retélécharger la page si elle a changé
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        # Déclenche l'option technique que nous avons activée sur votre iPhone (Clear-Site-Data)
        response.headers["Clear-Site-Data"] = '"cache", "storage"'
        
    return response
# --- 3. GESTION DE L'ÉTAT UTILISATEUR ---
class AppState:
    def __init__(self):
        self.step = 0
        self.lang = 'FR'
        self.choix = {}
        self.code_metier_affiche = ""
        self.art_cible = ""
        self.annexe_selectionnee = None
        self.annexes_cache = None          # <-- NOUVEAU : Cache pour éviter de bloquer le HUB au démarrage
        
## --- 4. COMPOSANTS D'AFFICHAGE RÉUTILISABLES ---

def get_linked_articles(num_article):
    """Récupère uniquement les cibles directes (ex: 128-2 vers 41-2)"""
    try:
        conn = sqlite3.connect('CCN_3239.db')
        conn.row_factory = sqlite3.Row
        # MODIFICATION 1 : On cherche uniquement la SOURCE (évite de remonter au parent)
        query = "SELECT cible FROM liens_inter_articles WHERE source = ?"
        liens = conn.execute(query, (str(num_article),)).fetchall()
        conn.close()
        
        return sorted(list(set(str(l['cible']) for l in liens)))
    except Exception:
        return []

def render_result(num_article, txt, current_state, set_step_func):
    """Affiche l'article et sa cascade avec précision"""
    if not num_article or num_article == "None":
        ui.label("⚠️ Article non renseigné").classes('text-orange-500 p-4 bg-orange-50 rounded-xl w-full')
        return

    # MODIFICATION 2 : On utilise une requête qui permet la cascade (LIKE)
    # tout en assurant l'ordre (le parent 41 avant les enfants 41-1)
    conn = sqlite3.connect('CCN_3239.db')
    conn.row_factory = sqlite3.Row
    query = """
        SELECT * FROM convention_collective 
        WHERE numero_article_isole = ? 
        OR numero_article_isole LIKE ? 
        ORDER BY numero_article_isole ASC
    """
    params = (str(num_article), f"{num_article}-%")
    articles = conn.execute(query, params).fetchall()
    conn.close()

    ui.label(f"Article {num_article}").classes('text-xl font-bold text-blue-700 w-full mb-4')
    
    for art in articles:
        # On identifie précisément l'article de la boucle pour ses liens propres
        id_art_boucle = str(art['numero_article_isole'])
        
        with ui.column().classes('article-card w-full mb-4'):
            ui.label(art['affichage_article']).classes('font-bold text-lg text-slate-900')
            
           # --- AFFICHAGE DU TEXTE SIMPLIFIÉ (Avec support HTML pour le rouge) ---
            res_col = 'texte_simplifie' if current_state.lang == 'FR' else 'texte_simplifie_en'
            if art[res_col]:
                with ui.column().classes('bg-blue-50 p-4 rounded-xl w-full my-3 border border-blue-100'):
                    
                    # 1. On définit les deux versions de la phrase
                    mention_fr = "Cet article a fait l'objet d'une modification en septembre 2025 (Avenant n° 10)"
                    mention_en = "This article was amended in September 2025 (Amendment No. 10)"
                    
                    texte_final = art[res_col]
                    couleur_rouge = "color: #ef4444; font-weight: bold;"

                    # 2. On applique le remplacement selon la langue détectée dans le texte
                    if mention_fr in texte_final:
                        texte_final = texte_final.replace(mention_fr, f'<span style="{couleur_rouge}">{mention_fr}</span>')
                    
                    if mention_en in texte_final:
                        texte_final = texte_final.replace(mention_en, f'<span style="{couleur_rouge}">{mention_en}</span>')
                    
                    # 3. Affichage avec ui.html pour interpréter les styles
                    ui.html(texte_final).classes('text-slate-800')
            
            # --- BLOC NAVIGATION INTER-ARTICLES ---
            try:
                # Vérification du socle commun (40 à 88)
                num_principal = int(id_art_boucle.split('-')[0].split('.')[0])
                is_socle_commun = 40 <= num_principal <= 88
            except ValueError:
                is_socle_commun = False

            if not is_socle_commun:
                liens = get_linked_articles(id_art_boucle)
                if liens:
                    with ui.row().classes('gap-2 mt-2 items-center'):
                        ui.label("🔗 Liens :").classes('text-xs font-bold text-slate-500')
                        for n_lie in liens:
                            ui.button(n_lie, on_click=lambda n=n_lie: set_step_func('DIRECT', {'art_cible': n})) \
                                .props('outline dense size=sm color=primary') \
                                .classes('rounded-full px-3 text-[10px]')

            # Texte officiel
            with ui.expansion(txt.get('official', '⚖️ Texte officiel')).classes('w-full text-sm text-slate-500 border-t mt-4'):
                ui.markdown(art['texte_integral']).classes('text-[12px] italic')
                
# --- 5. MOTEUR DE NAVIGATION ET LOGIQUE D'INTERFACE ---
@ui.refreshable
def build_ui(state, h_zone, c_zone):
    h_zone.clear()
    c_zone.clear()
    c_zone.style('margin-top: 44px;' if state.step != 0 else 'margin-top: 0px;')
    
    def set_step(s, data=None):
        state.step = s
        if data: 
            # Redirection métier vers colonnes réelles pour le SQL
            if 'colonne_metier' in data:
                m = data['colonne_metier']
                if m in ["art_ap", "art_av"]: data['colonne_metier'] = "art_ef"
                elif m == "art_cesu": data['colonne_metier'] = "art_sc"
            
            state.choix.update(data)
            
            if 'colonne_metier' in data:
                mapping = {
                    "art_am": "Socle Assistant Maternel",
                    "art_sc": "Socle Commun",
                    "art_ef": "Salarié Particulier Employeur"
                }
                state.code_metier_affiche = mapping.get(data['colonne_metier'], "CCN 3239")
            
            if 'art_cible' in data: state.art_cible = data['art_cible']
            if 'annexe_id' in data: state.annexe_selectionnee = data['annexe_id']
    def set_step(s, data=None):
        """Mise à jour sélective de l'état applicatif et routage des alias métiers"""
        state.step = s
        if data: 
            if 'colonne_metier' in data:
                m = data['colonne_metier']
                if m in ["art_ap", "art_av"]: data['colonne_metier'] = "art_ef"
                elif m == "art_cesu": data['colonne_metier'] = "art_sc"
            
            state.choix.update(data)
            
            if 'colonne_metier' in data:
                mapping = {
                    "art_am": "Socle Assistant Maternel",
                    "art_sc": "Socle Commun",
                    "art_ef": "Salarié Particulier Employeur"
                }
                state.code_metier_affiche = mapping.get(data['colonne_metier'], "CCN 3239")
            
            if 'art_cible' in data: state.art_cible = data['art_cible']
            if 'annexe_id' in data: state.annexe_selectionnee = data['annexe_id']

        # --- AJOUT ICI : Envoi automatique du clic d'écran à Google Analytics ---
        try:
            ui.run_javascript(f"gtag('event', 'screen_view', {{'screen_name': 'Ecran_{s}'}});")
        except Exception:
            pass
        
        build_ui.refresh()

    col_filtre = state.choix.get('colonne_metier', 'art_sc')
    
    UI_TEXT = {
        'FR': {
            'home': '🏠 ACCUEIL', 'search_label': '🔍 Recherche directe (Ex: 139)', 'search_btn': 'Aller',
            'step1_title': 'Quel est votre métier ?', 'step2_title': 'Quelle est votre situation ?', 
            'gestion': 'LA GESTION DU CONTRAT', 'fin': 'LA FIN DU CONTRAT', 
            'annexes_btn': '📚 ANNEXES (Résumés & PDF)', 'back': '⬅️ RETOUR',
            'official_pdf': '📄 Consulter le PDF Officiel', 'official': '⚖️ Texte officiel',
            'game_btn': 'TESTEZ VOS CONNAISSANCES', 'direct_btn': 'ARTICLE CCN 3239 EN 1 CLIC'
        },
        'EN': {
            'home': '🏠 HOME', 'search_label': '🔍 Direct search (Ex: 139)', 'search_btn': 'Go',
            'step1_title': 'What is your job ?', 'step2_title': 'What is your situation ?', 
            'gestion': 'CONTRACT MANAGEMENT', 'fin': 'END OF CONTRACT', 
            'annexes_btn': '📚 ANNEXES (Summary & PDF)', 'back': '⬅️ BACK',
            'official_pdf': '📄 View Official PDF', 'official': '⚖️ Official text',
            'game_btn': 'TEST YOUR KNOWLEDGE', 'direct_btn': 'CCN 3239 ARTICLE IN 1 CLICK'
        }
    }
    txt = UI_TEXT[state.lang]

    # --- 6. CONSTRUCTION DE L'ENTÊTE (H_ZONE) ---
    with h_zone:
        if state.step != 0:
            h_zone.set_visibility(True)  # On l'affiche sur les autres étapes
            with ui.row().classes('w-full px-4 py-1 header-row items-center'):
                ui.label(state.code_metier_affiche if state.code_metier_affiche else 'CCN 3239') \
                    .classes('text-blue-600 font-black text-base truncate flex-shrink')
                with ui.row().classes('gap-2 flex-nowrap items-center flex-none'):
                    ui.button('🇫🇷', on_click=lambda: (setattr(state, 'lang', 'FR'), build_ui.refresh())).props('flat').classes('text-xl p-0')
                    ui.button('🇬🇧', on_click=lambda: (setattr(state, 'lang', 'EN'), build_ui.refresh())).props('flat').classes('text-xl p-0')
        else:
            h_zone.set_visibility(False)  # On le masque TOTALEMENT à l'étape 0
            
    # --- 7. CONSTRUCTION DU CONTENU DYNAMIQUE (C_ZONE) ---
    with c_zone:
        # La suite de ton code...
       # --- ÉTAPE 0 : ÉCRAN D'ACCUEIL CORRIGÉ (INTERLIGNES & POSTION IPHONE) ---
        if state.step == 0:
            h_zone.set_visibility(False)
            
            def start_app():
                state.step = 1
                build_ui.refresh()

            # Le conteneur s'adapte à la largeur max de l'application
            with ui.column().classes('w-full max-w-md mx-auto items-center justify-start no-wrap p-0 bg-[#b91c1c] relative cursor-pointer') \
                .on('click', start_app):
                
                # L'image dicte la hauteur naturelle sans déformer l'écran
                ui.image('/static/accueil.jpg?v=2').classes('w-full h-auto pointer-events-none')
                
                # L'accroche avec un positionnement top en pourcentage et un line-height très serré
                with ui.column().classes('absolute top-[7%] left-0 right-0 items-center justify-center px-4 pointer-events-none'):
                    if state.lang == 'FR':
                        accroche = """
                        <div style='color: #ffffff; font-weight: 900; font-size: 22px; line-height: 1.1; text-shadow: 1px 1px 4px rgba(0,0,0,0.4);'>CONTRAT DE TRAVAIL S.P.E :</div>
                        <div style='color: #ffffff; font-weight: 500; font-size: 20px; line-height: 1.1; margin-top: 5px; text-shadow: 1px 1px 4px rgba(0,0,0,0.4);'>suivez le fil</div>
                        <div style='color: #ffffff; font-weight: 500; font-size: 20px; line-height: 1.1; text-shadow: 1px 1px 4px rgba(0,0,0,0.4);'>selon votre profil.</div>
                        """
                    else:
                        accroche = """
                        <div style='color: #ffffff; font-weight: 900; font-size: 22px; line-height: 1.1; text-shadow: 1px 1px 4px rgba(0,0,0,0.4);'>S.P.E EMPLOYMENT CONTRACT:</div>
                        <div style='color: #ffffff; font-weight: 500; font-size: 20px; line-height: 1.1; margin-top: 5px; text-shadow: 1px 1px 4px rgba(0,0,0,0.4);'>follow the guide</div>
                        <div style='color: #ffffff; font-weight: 500; font-size: 20px; line-height: 1.1; text-shadow: 1px 1px 4px rgba(0,0,0,0.4);'>according to your profile.</div>
                        """
                    ui.html(accroche).classes('text-center uppercase tracking-wide')
            return
        

        if state.step not in [0, 1]:
            ui.button(txt['home'], on_click=lambda: set_step(1)) \
                .props('flat dense icon=home color=primary') \
                .classes('w-full mb-4 text-slate-500 border-b pb-2')

        if state.step == 1:
            # On définit une hauteur minimale de 450px et on ajuste le padding (p-12 au lieu de p-8)
            with ui.dialog() as direct_dialog, ui.card().classes('items-center p-12 rounded-3xl') \
                .style('width: 350px !important; min-height: 450px !important; justify-content: center !important;'):
                
                # On agrandit la marge sous le titre
                ui.label(txt['search_label']).classes('font-bold text-center text-slate-800 text-2xl mb-6')
                
                # On donne de l'espace autour de l'input
                i_direct = ui.input(placeholder="---").classes('w-full text-center font-bold') \
                    .style('font-size: 40px !important; height: 80px !important; margin-bottom: 20px !important;')
                
                # Bouton plus haut également
                ui.button(txt['search_btn'], on_click=lambda: (set_step('DIRECT', {'art_cible': i_direct.value}), direct_dialog.close())) \
                    .classes('w-full py-6 mt-6 bg-blue-900 text-white rounded-xl font-bold text-lg')

            METIERS_DATA = [
                {"c": "art_am", "fr": "Assistant Maternel", "en": "Childminder", "icon": "fa-baby-carriage"},
                {"c": "art_ap", "fr": "Assistant Parental", "en": "Nanny", "icon": "fa-baby"},
                {"c": "art_ef", "fr": "Employé Familial", "en": "Family Employee", "icon": "fa-house-user"},
                {"c": "art_av", "fr": "Assistant de Vie", "en": "Life Assistant", "icon": "fa-wheelchair"},
                {"c": "art_cesu", "fr": "Autres métiers CESU", "en": "Other jobs (CESU)", "icon": "fa-briefcase"},
                {"c": "DIRECT", "fr": "ACCÈS DIRECT À UN ARTICLE", "en": "DIRECT SEARCH", "icon": "fa-magnifying-glass", "is_special": True},
                {"c": "LISTE_ANNEXES", "fr": "ANNEXES + AVENANTS 2026 PDF", "en": "PDF ANNEXES + AMENDMENTS 2026", "icon": "fa-file-pdf", "is_special": True},
                {"c": "JEUX", "fr": "TESTEZ VOS CONNAISSANCES", "en": "TEST YOUR KNOWLEDGE", "icon": "fa-gamepad", "is_special": True}
            ]

            # --- Extrait de la ligne 232 corrigée ---
            with ui.element('div').classes('grid-container w-full'):
                for m in METIERS_DATA:
                    label_affiche = m['fr'] if state.lang == 'FR' else m['en']
                    is_special = m.get('is_special', False)
                    
                    # Définition des styles (st) et actions
                    if m['c'] == "DIRECT": 
                        on_click_action = lambda: direct_dialog.open()
                        st = 'border: 2px solid #10b981 !important;'
                    elif m['c'] == "JEUX":
                        on_click_action = lambda c=m['c']: set_step(c)
                        st = 'border: 2px solid #ef4444 !important;'  # Rouge (Tailwind red-500)
                    elif is_special: 
                        on_click_action = lambda c=m['c']: set_step(c)
                        st = 'border: 2px solid #3b82f6 !important;'
                    else: 
                        on_click_action = lambda c=m['c'], l=label_affiche: set_step(2, {'colonne_metier': c, 'label_metier': l})
                        st = 'border: 2px solid #e2e8f0 !important;'

                    # LA LIGNE 232 DOIT ÊTRE ALIGNÉE ICI :
                    with ui.card().classes('q-card h-24 items-center justify-center text-center cursor-pointer shadow-sm').style(st).on('click', on_click_action):
                        ui.html(f'<i class="fa-solid {m["icon"]} mb-1 text-slate-700" style="font-size: 1.2rem;"></i>')
                        ui.label(label_affiche).classes('text-xs font-bold uppercase leading-tight text-slate-800 px-1')

        elif state.step == 2:
            ui.label(txt['step2_title']).classes('text-lg font-bold text-slate-700 w-full mb-2 px-2')
            query_filter = f"WHERE {col_filtre} IS NOT NULL AND {col_filtre} != ''"
            options = db.fetch_options("etape_vie", state.lang, query_filter)
            with ui.column().classes('w-full'):
                for o in options:
                    is_life = "Vie" in o or "Life" in o
                    label_bouton = txt['gestion'] if is_life else txt['fin']
                    ui.button(label_bouton, on_click=lambda o=o: set_step(3, {'etape_val': o})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(1)).props('flat').classes('w-full mt-4')

        elif state.step == 3:
            f = f"WHERE (etape_vie = '{state.choix['etape_val']}' OR etape_vie_en = '{state.choix['etape_val']}') AND {col_filtre} != ''"
            fams = db.fetch_options("famille", state.lang, f)
            with ui.column().classes('w-full'):
                for f_v in fams: ui.button(f_v, on_click=lambda f_v=f_v: set_step(4, {'famille_val': f_v})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(2)).props('flat').classes('w-full mt-4')

        elif state.step == 4:
            f = f"WHERE (famille = '{state.choix['famille_val']}' OR famille_en = '{state.choix['famille_val']}') AND {col_filtre} != ''"
            thms = db.fetch_options("theme", state.lang, f)
            with ui.column().classes('w-full'):
                for t in thms: ui.button(t, on_click=lambda t=t: set_step(5, {'theme': t})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(3)).props('flat').classes('w-full mt-4')

        elif state.step == 5:
            col_q = "question_claire" if state.lang == 'FR' else "question_en"
            col_th = "theme" if state.lang == 'FR' else "theme_en"
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, {col_q} FROM questions WHERE {col_th} = ? AND {col_filtre} != ''", (state.choix['theme'],))
            questions = cursor.fetchall()
            conn.close()
            for q in questions:
                ui.button(q[1], on_click=lambda q_id=q[0]: set_step(6, {'id_question': q_id})).classes('w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-left mb-3 font-medium')
            ui.button(txt['back'], on_click=lambda: set_step(4)).props('flat').classes('w-full mt-4')

        elif state.step == 6:
            num_art = db.get_article_from_question(state.choix['id_question'], state.choix['colonne_metier'])
            render_result(num_art, txt, state, set_step) # On ajoute set_step ici
            ui.button(txt['back'], on_click=lambda: set_step(5)).props('flat').classes('w-full mt-4')

        elif state.step == 'DIRECT':
            render_result(state.art_cible, txt, state, set_step) # On ajoute set_step ici
            ui.button(txt['back'], on_click=lambda: set_step(1)).props('flat').classes('w-full mt-4')

        # --- ÉTAPE : LISTE DES ANNEXES (GRILLE) ---
        elif state.step == 'LISTE_ANNEXES':
            ui.label(txt['annexes_btn']).classes('text-xl font-bold mb-4')
            conn = sqlite3.connect('CCN_3239.db', timeout=20)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT numero, titre FROM annexes ORDER BY CAST(numero AS INTEGER)").fetchall()
            conn.close()
            
            with ui.element('div').classes('grid-container w-full'):
                for row in rows:
                    n, t = row['numero'], row['titre']
                    with ui.card().classes('w-full h-28 bg-white text-black border-2 border-slate-300 rounded-2xl shadow-md p-0 overflow-hidden cursor-pointer') \
                        .on('click', lambda n=n: set_step('VOIR_ANNEXE', {'annexe_id': n})):
                        with ui.column().classes('items-center justify-center p-3 gap-1 w-full text-center h-full'):
                            ui.label(f"ANNEXE N°{n}").classes('text-[10px] font-black text-blue-600 uppercase')
                            ui.label(t.upper()).classes('text-[10px] font-bold leading-tight text-slate-700 uppercase')
                
                # Le 8ème cartouche transformé en bouton vers l'Avenant 10
                with ui.card().classes('w-full h-28 bg-red-50 text-red-600 border-2 border-red-200 rounded-2xl shadow-sm p-0 overflow-hidden cursor-pointer') \
                    .on('click', lambda: set_step('VOIR_AVENANT_10')):
                    with ui.column().classes('items-center justify-center p-3 gap-1 w-full text-center h-full'):
                        ui.html('<i class="fa-solid fa-file-signature" style="font-size: 1rem;"></i>')
                        ui.label('Avenant n° 10 du\n9 septembre 2025').classes('text-[10px] font-black leading-tight uppercase').style('white-space: pre-line;')

        # --- ÉTAPE : DÉTAIL D'UNE ANNEXE CLASSIQUE ---
        elif state.step == 'VOIR_ANNEXE':
            conn = sqlite3.connect('CCN_3239.db', timeout=20)
            conn.row_factory = sqlite3.Row
            res = conn.execute("SELECT titre, resume_fr, resume_en, numero FROM annexes WHERE numero = ?", (state.annexe_selectionnee,)).fetchone()
            conn.close()
            if res:
                resume = res['resume_fr'] if state.lang == 'FR' else res['resume_en']
                with ui.column().classes('annexe-container w-full'):
                    with ui.element('div').classes('annexe-title-section'):
                        ui.label(f"ANNEXE N°{res['numero']}").classes('text-blue-600 font-bold uppercase text-xs tracking-widest')
                        ui.label(res['titre']).classes('text-2xl font-black text-slate-800 leading-tight')
                    with ui.element('div').classes('annexe-card-info'):
                        ui.markdown(resume if resume else "Résumé à venir...").classes('text-slate-700 leading-relaxed')
                    with ui.card().classes('w-full bg-red-50 p-4 border border-red-100 rounded-2xl items-center mt-4'):
                        ui.label(txt['official_pdf']).classes('text-red-900 font-bold mb-2')
                        pdf_url = f"/static/Annexe_{res['numero']}.pdf"
                        ui.button("CONSULTER LE PDF", icon='visibility', on_click=lambda: ui.navigate.to(pdf_url, new_tab=True)) \
                            .props('elevated color=red-800').classes('rounded-full')
                            
                    ui.button(txt['back'], on_click=lambda: set_step('LISTE_ANNEXES')).props('flat icon=arrow_back').classes('w-full text-slate-400 mt-4')

        # --- ÉTAPE : PAGE SPÉCIALE AVENANT 10 ---
        elif state.step == 'VOIR_AVENANT_10':
            with ui.column().classes('w-full items-center gap-4'):
                ui.label("AVENANT N° 10").classes('text-blue-600 font-bold uppercase text-xs tracking-widest')
                ui.label("Rupture du contrat de travail du fait de l’inaptitude").classes('text-xl font-black text-slate-800 text-center leading-tight')
                
                with ui.card().classes('w-full p-6 bg-white border-2 border-slate-100 rounded-3xl shadow-sm items-center'):
                    ui.label("Consulter le document :").classes('font-bold text-slate-500 mb-4')
                    ui.button("🇫🇷 FRANÇAIS", on_click=lambda: ui.navigate.to('/static/avenant_inaptitude_FR.pdf', new_tab=False)) \
                        .classes('w-full py-3 rounded-xl mb-3').props('elevated color=blue-900')
                    ui.button("🇬🇧 ENGLISH", on_click=lambda: ui.navigate.to('/static/avenant_inaptitude_EN.pdf', new_tab=False)) \
                        .classes('w-full py-3 rounded-xl').props('outline color=blue-900')

                ui.button(txt['back'], on_click=lambda: set_step('LISTE_ANNEXES')).props('flat icon=arrow_back').classes('w-full text-slate-400 mt-4')

        elif state.step == 'JEUX':
            ui.label(txt['game_btn']).classes('text-xl font-bold mb-6 text-slate-800 w-full text-center')
            with ui.column().classes('w-full gap-4'):
                ui.button('LEXIQUE ↔ DÉFINITIONS', on_click=lambda: set_step('GAME_ASSOC')).classes(css.BTN_STYLE)
                ui.button('GLOSSAIRE FRANÇAIS ↔ ANGLAIS', on_click=lambda: set_step('GAME_TRAD')).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(1)).props('flat icon=arrow_back').classes('w-full text-slate-400 mt-8')

        elif state.step == 'GAME_ASSOC':
            if 'game_assoc' not in state.choix:
                state.choix['game_assoc'] = game_definitions.AssociationGame()
            game_definitions.render_ui(state.choix['game_assoc'])
            ui.button(txt['back'], on_click=lambda: set_step('JEUX')).props('flat icon=arrow_back').classes('w-full text-slate-400 mt-4')

        elif state.step == 'GAME_TRAD':
            if 'game_trad' not in state.choix:
                state.choix['game_trad'] = game_translation.TranslationGame()
            game_translation.render_ui(state.choix['game_trad'])
            ui.button(txt['back'], on_click=lambda: set_step('JEUX')).props('flat icon=arrow_back').classes('w-full text-slate-400 mt-4')

# --- 8. INITIALISATION DE LA PAGE PRINCIPALE ---
@ui.page('/')
def main_page():
    # 1. Votre NOUVEL ID de mesure officiel et définitif
    ga_id = "G-71B4Z4QCLZ"  

    # 2. Injection du script conforme (sans pop-up utilisateur)
    ui.add_head_html(f'''
        <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          
          // Configuration du consentement invisible pour l'Europe (Corrigé)
          gtag('consent', 'default', {{
            'ad_storage': 'denied',
            'ad_user_data': 'denied',
            'ad_personalization': 'denied',
            'analytics_storage': 'granted'
          }});
          
          gtag('js', new Date());
          gtag('config', '{ga_id}');
        </script>

        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>{css.STYLE_CSS}</style>
        <style>
            /* On double les accolades ici car on est dans une f-string */
            .header-row .q-btn__content {{ font-size: 1.25rem !important; }}
        </style>
    ''')
    game_definitions.inject_custom_style()
    user_state = AppState()
    
    # Zone d'en-tête
    h_zone = ui.column().classes('w-full sticky-header')
    
    # Zone de contenu
    c_zone = ui.column().classes('w-full max-w-md mx-auto p-0 gap-0 items-center')
    
    build_ui(user_state, h_zone, c_zone)
# --- 9. CONFIGURATION ET LANCEMENT SERVEUR ---
ui.run(
    title="Guide CCN", 
    host='0.0.0.0', 
    # FORCEZ LE PORT 8080 ICI
    port=int(os.environ.get("PORT", 8080)), 
    reload=False,
    reconnect_timeout=30,
    show=False 
)
