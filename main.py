from nicegui import app, ui
import sql_manager as db
import css
import os
import sqlite3

# --- CONFIGURATION PDF ---
# Assure-toi que le dossier 'static' existe sur ton GitHub
app.add_static_files('/static', 'static')

class AppState:
    def __init__(self):
        self.step = 1
        self.lang = 'FR'
        self.choix = {}
        self.code_metier_affiche = ""
        self.art_cible = ""
        self.annexe_selectionnee = None 

state = AppState()

def set_step(s, data=None):
    state.step = s
    if data: 
        state.choix.update(data)
        if 'colonne_metier' in data:
            col = data['colonne_metier']
            mapping = {
                "art_am": "Socle Assistant Maternel",
                "art_sc": "Socle Commun",
                "art_ef": "Salarié Particulier Employeur"
            }
            state.code_metier_affiche = mapping.get(col, "CCN 3239")
        if 'art_cible' in data:
            state.art_cible = data['art_cible']
        if 'annexe_id' in data:
            state.annexe_selectionnee = data['annexe_id']
    build_ui.refresh()

ui.add_head_html(f'''
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>{css.STYLE_CSS}</style>
''')

# --- FONCTION DE RENDU DES ARTICLES ---
def render_result(num_article, txt):
    if not num_article or num_article == "None":
        ui.label("⚠️ Article non renseigné").classes('text-orange-500 p-4 bg-orange-50 rounded-xl w-full')
        return
    articles = db.fetch_articles_complet(num_article)
    ui.label(f"Article {num_article}").classes('text-xl font-bold text-blue-700 w-full mb-4')
    for art in articles:
        with ui.column().classes('article-card w-full'):
            ui.label(art['affichage_article']).classes('font-bold text-lg text-slate-900')
            res_col = 'texte_simplifie' if state.lang == 'FR' else 'texte_simplifie_en'
            if art[res_col]:
                with ui.column().classes('bg-blue-50 p-4 rounded-xl w-full my-3 border border-blue-100'):
                    ui.label(art[res_col]).classes('text-slate-800')
            with ui.expansion(txt.get('official', '⚖️ Texte officiel')).classes('w-full text-sm text-slate-500 border-t mt-4'):
                ui.markdown(art['texte_integral']).classes('text-[12px] italic')

# --- ZONE PRINCIPALE RAFRAÎCHISSABLE ---
@ui.refreshable
def build_ui():
    content_area.clear()
    header_area.clear()
    
    col_filtre = state.choix.get('colonne_metier', 'art_sc')
    
    UI_TEXT = {
        'FR': {
            'home': '🏠 ACCUEIL',
            'search_label': '🔍 Recherche directe (Ex: 139)',
            'search_btn': 'Aller',
            'step1_title': 'Quel est votre métier ?',
            'step2_title': 'Quelle est votre situation ?', 
            'gestion': 'LA GESTION DU CONTRAT',              
            'fin': 'LA FIN DU CONTRAT',                    
            'annexes_btn': '📚 ANNEXES (Résumés & PDF)',
            'back': '⬅️ RETOUR',
            'official_pdf': '📄 Consulter le PDF Officiel',
            'official': '⚖️ Texte officiel'
        },
        'EN': {
            'home': '🏠 HOME',
            'search_label': '🔍 Direct search (Ex: 139)',
            'search_btn': 'Go',
            'step1_title': 'What is your job ?',
            'step2_title': 'What is your situation ?',   
            'gestion': 'CONTRACT MANAGEMENT',              
            'fin': 'END OF CONTRACT',                
            'annexes_btn': '📚 ANNEXES (Summary & PDF)',
            'back': '⬅️ BACK',
            'official_pdf': '📄 View Official PDF',
            'official': '⚖️ Official text'
        }
    }
    txt = UI_TEXT[state.lang]

    with header_area:
        with ui.row().classes('w-full items-center justify-between px-4 py-3'):
            ui.label(state.code_metier_affiche if state.code_metier_affiche else 'CCN 3239').classes('text-blue-600 font-black text-lg')
            with ui.row().classes('gap-3'):
                ui.button('🇫🇷', on_click=lambda: (setattr(state, 'lang', 'FR'), build_ui.refresh())).props('flat').classes('text-2xl p-0')
                ui.button('🇬🇧', on_click=lambda: (setattr(state, 'lang', 'EN'), build_ui.refresh())).props('flat').classes('text-2xl p-0')

    with content_area:
        if state.step not in ['DIRECT', 6, 'LISTE_ANNEXES', 'VOIR_ANNEXE']:
            with ui.expansion(txt['search_label']).classes('w-full border-2 rounded-2xl mb-4'):
                with ui.row().classes('w-full items-center p-3'):
                    s_input = ui.input(placeholder="Ex: 139").classes('flex-grow')
                    ui.button(txt['search_btn'], on_click=lambda: set_step('DIRECT', {'art_cible': s_input.value})).props('flat').classes('font-bold')

        if state.step != 1:
            ui.button(txt['home'], on_click=lambda: (state.__init__(), build_ui.refresh())).props('flat icon=home').classes('text-blue-500 font-bold mb-2 self-start')

        if state.step == 1:
            METIERS_DATA = [
                {"c": "art_am", "fr": "🍼 Assistant Maternel", "en": "🍼 Childminder"},
                {"c": "art_ef", "fr": "👶 Assistant Parental", "en": "👶 Nanny / Parental Assistant"},
                {"c": "art_ef", "fr": "🏠 Employé Familial", "en": "🏠 Family Employee"},
                {"c": "art_ef", "fr": "👵 Assistant de Vie", "en": "👵 Life Assistant"},
                {"c": "art_sc", "fr": "Autres métiers payés CESU", "en": "Other jobs paid by CESU"}
            ]
            ui.label(txt['step1_title']).classes('text-xl font-bold text-slate-800 w-full mb-2')
            with ui.element('div').classes('grid-container'):
                for m in METIERS_DATA:
                    label_affiche = m['fr'] if state.lang == 'FR' else m['en']
                    ui.button(label_affiche, 
                              on_click=lambda m=m, l=label_affiche: set_step(2, {
                                  'colonne_metier': m['c'], 
                                  'label_metier': l
                              })).classes(css.BTN_STYLE)
            ui.separator().classes('my-4')
            ui.button(txt['annexes_btn'], on_click=lambda: set_step('LISTE_ANNEXES')).classes('w-full py-4 bg-slate-800 text-white rounded-2xl font-bold shadow-lg')
            
        elif state.step == 'LISTE_ANNEXES':
            ui.label(txt['annexes_btn']).classes('text-xl font-bold mb-1')
            ui.label('Documents à jour au 31 décembre 2024').classes('text-xs text-red-600 font-bold mb-4 px-2 italic uppercase border-l-2 border-red-600')
            conn = sqlite3.connect('CCN_3239.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT numero, titre FROM annexes ORDER BY CAST(numero AS INTEGER)")
            rows = cursor.fetchall()
            conn.close()
            with ui.element('div').classes('grid-container w-full'):
                for row in rows:
                    n, t = row['numero'], row['titre']
                    with ui.card().classes('w-full h-28 bg-white text-black border-2 border-slate-300 rounded-2xl shadow-md hover:bg-blue-50 cursor-pointer p-0 overflow-hidden') \
                        .on('click', lambda n=n: set_step('VOIR_ANNEXE', {'annexe_id': n})):
                        with ui.column().classes('items-center justify-center p-3 gap-1 w-full text-center h-full'):
                            ui.label(f"ANNEXE N°{n}").classes('text-[10px] font-black text-blue-600 uppercase tracking-widest')
                            ui.label(t.upper()).classes('text-[10px] font-bold leading-tight text-slate-700 uppercase')

        elif state.step == 'VOIR_ANNEXE':
            conn = sqlite3.connect('CCN_3239.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT titre, resume_fr, resume_en, numero FROM annexes WHERE numero = ?", (state.annexe_selectionnee,))
            res = cursor.fetchone()
            conn.close()
            if res:
                resume = res['resume_fr'] if state.lang == 'FR' else res['resume_en']
                ui.label(res['titre']).classes('text-xl font-black text-blue-900 mb-4 px-2')
                with ui.card().classes('w-full p-6 bg-white border-t-4 border-blue-900 shadow-md rounded-2xl'):
                    ui.markdown(resume if resume else "Résumé à venir...")
                pdf_url = f"/static/Annexe_{res['numero']}.pdf"
                with ui.card().classes('w-full bg-red-50 p-4 border border-red-100 rounded-2xl mt-6 items-center'):
                    ui.label(txt['official_pdf']).classes('text-red-900 font-bold mb-2')
                    ui.button(icon='download', on_click=lambda: ui.download(pdf_url)).props('round flat color=red-900')

        elif state.step == 2:
            ui.label(txt['step2_title']).classes('text-lg font-bold text-slate-700 w-full mb-2 px-2')
            f = f"WHERE {col_filtre} IS NOT NULL AND {col_filtre} != ''"
            options = db.fetch_options("etape_vie", state.lang, f)
            with ui.element('div').classes('grid-container'):
                for o in options:
                    label_bouton = txt['gestion'] if ("Vie" in o or "Life" in o) else txt['fin']
                    ui.button(label_bouton, on_click=lambda o=o: set_step(3, {'etape_val': o})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(1)).props('flat').classes('w-full mt-4')

        elif state.step == 3:
            f = f"WHERE (etape_vie = '{state.choix['etape_val']}' OR etape_vie_en = '{state.choix['etape_val']}') AND {col_filtre} != ''"
            fams = db.fetch_options("famille", state.lang, f)
            with ui.element('div').classes('grid-container'):
                for f_v in fams: ui.button(f_v, on_click=lambda f_v=f_v: set_step(4, {'famille_val': f_v})).classes(css.BTN_STYLE)
            ui.button(txt['back'], on_click=lambda: set_step(2)).props('flat').classes('w-full mt-4')

        elif state.step == 4:
            f = f"WHERE (famille = '{state.choix['famille_val']}' OR famille_en = '{state.choix['famille_val']}') AND {col_filtre} != ''"
            thms = db.fetch_options("theme", state.lang, f)
            with ui.element('div').classes('grid-container'):
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
            render_result(num_art, txt)
            ui.button(txt['back'], on_click=lambda: set_step(5)).props('flat').classes('w-full mt-4')

        elif state.step == 'DIRECT':
            render_result(state.art_cible, txt)

# --- STRUCTURE FIXE ---
header_area = ui.column().classes('w-full sticky-header')
content_area = ui.column().classes('w-full max-w-md mx-auto p-4 gap-4 items-center')

# Premier lancement de l'UI
build_ui()

# --- CONFIGURATION SERVEUR (LES DERNIÈRES LIGNES) ---
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Guide CCN", host='0.0.0.0', port=8080, reload=False)
