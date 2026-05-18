from nicegui import ui
import lexique_manager as lex
import random
import os

# --- SÉCURITÉ RÉSEAU ---
def kill_port(port):
    """Tue le processus occupant le port pour éviter l'erreur [Errno 48]"""
    try:
        os.system(f"lsof -ti:{port} | xargs kill -9 > /dev/null 2>&1")
    except:
        pass

# --- STYLE CSS ADAPTATIF ---
# --- STYLE CSS ADAPTATIF ---
def inject_custom_style():
    ui.add_head_html(f'''
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
        <style>
            .montserrat {{ font-family: 'Montserrat', sans-serif !important; }}
            .main-container {{
                height: 92dvh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}
            .box-card {{ 
                background-color: white; border-radius: 10px; padding: 6px; 
                cursor: pointer; display: flex; align-items: center; justify-content: center;
                transition: all 0.1s; flex-grow: 1; margin-bottom: 6px; min-height: 0; 
            }}
            .box-mot {{ border: 2px solid #1e3a8a !important; color: #1e3a8a !important; }}
            .box-def {{ border: 2px solid #15803d !important; color: #15803d !important; }}
            .responsive-text {{
                font-size: clamp(12px, 3.5vw, 15px);
                line-height: 1.2;
                text-align: center;
            }}
            .selected-blue {{ background-color: #dbeafe !important; border-width: 3px !important; }}
            .selected-green {{ background-color: #dcfce7 !important; border-width: 3px !important; }}
            .matched {{ opacity: 0.1 !important; pointer-events: none !important; border-style: dashed !important; }}
            
            /* IMPORTANT : On cible .lang-selector pour que seuls les drapeaux 
               soient géants. Les boutons ACCUEIL et RETOUR resteront normaux.
            */
            .lang-selector .q-btn__content {{
                font-size: 1.5rem !important; 
            }}

            .q-btn-group {{
                padding: 5px 20px;
                background-color: #f8fafc;
                border-radius: 20px;
                gap: 20px;
            }}
        </style>
    ''')

# --- LOGIQUE DU JEU ---
class AssociationGame:
    def __init__(self):
        self.nb_paires = 5 
        self.lang = 'FR'
        self.reset_game()

    def reset_game(self):
        raw = lex.get_random_lexicon_pair(self.nb_paires, self.lang)
        self.mots = []
        self.defs = []
        for item in raw:
            key = str(item['mot']).strip()
            self.mots.append({'text': key, 'match': key})
            self.defs.append({'text': str(item['def']).strip(), 'match': key})
        
        random.shuffle(self.mots)
        random.shuffle(self.defs)
        self.sel_mot = None
        self.sel_def = None
        self.found = set()

    def check(self):
        if self.sel_mot and self.sel_def:
            if self.sel_mot['match'] == self.sel_def['match']:
                ui.notify('Bravo !' if self.lang == 'FR' else 'Correct!', type='positive')
                self.found.add(self.sel_mot['match'])
            else:
                ui.notify('Réessayez' if self.lang == 'FR' else 'Try again', type='negative')
            self.sel_mot = None
            self.sel_def = None
            render_ui.refresh()

# --- INTERFACE UTILISATEUR ---
@ui.refreshable
def render_ui(game):
    with ui.column().classes('w-full items-center p-0 gap-0 montserrat'):
        
        # --- SÉLECTEUR DE LANGUE (Aligné correctement) ---
        # --- SÉLECTEUR DE LANGUE (Aligné correctement avec classe spécifique) ---
        with ui.row().classes('w-full justify-center items-center mb-4'):
            ui.toggle(
                {'FR': '🇫🇷', 'EN': '🇬🇧'}, 
                value=game.lang, 
                on_change=lambda e: (
                    setattr(game, 'lang', e.value), 
                    game.reset_game(), 
                    render_ui.refresh()
                )
            ).props('flat').classes('lang-selector') # <--- L'ajout magique est ici

        # Le sélecteur de langue (s'il y en a un doublon, retirez-le)
        # Assurez-vous que le titre a mt-0
        ui.label("Associez les termes" if game.lang == 'FR' else "Match the terms") \
            .classes('text-lg font-black text-center w-full mb-2 mt-0 text-slate-800')
        
        with ui.row().classes('w-full no-wrap gap-2 flex-grow items-stretch'):
            # Colonne MOTS
            with ui.column().classes('w-[35%] gap-0 items-stretch'):
                ui.label("MOTS" if game.lang == 'FR' else "WORDS").classes('text-sm font-black opacity-40 mb-1')
                for m in game.mots:
                    is_done = m['match'] in game.found
                    active = game.sel_mot == m
                    card = ui.card().classes('box-card box-mot shadow-none')
                    if is_done: card.classes('matched')
                    if active: card.classes('selected-blue')
                    with card:
                        ui.label(m['text']).classes('responsive-text font-bold')
                    card.on('click', lambda m=m: (setattr(game, 'sel_mot', m), game.check(), render_ui.refresh()))

            # Colonne DÉFINITIONS
            with ui.column().classes('w-[65%] gap-0 items-stretch'):
                ui.label("DÉFINITIONS").classes('text-sm font-black opacity-40 mb-1')
                for d in game.defs:
                    is_done = d['match'] in game.found
                    active = game.sel_def == d
                    card = ui.card().classes('box-card box-def shadow-none')
                    if is_done: card.classes('matched')
                    if active: card.classes('selected-green')
                    with card:
                        ui.label(d['text']).classes('responsive-text font-bold')
                    card.on('click', lambda d=d: (setattr(game, 'sel_def', d), game.check(), render_ui.refresh()))

        if len(game.found) == game.nb_paires:
            ui.button("REJOUER" if game.lang == 'FR' else "PLAY AGAIN", on_click=lambda: (game.reset_game(), render_ui.refresh())) \
                .classes('w-full py-3 bg-blue-900 text-white rounded-xl font-bold mt-2 shadow-lg')

@ui.page('/')
def main():
    inject_custom_style()
    
    # On utilise une colonne avec gap-0 pour supprimer l'espace entre Accueil et le reste
    with ui.column().classes('w-full items-center gap-0'):
        
        # 1. Votre bouton ACCUEIL (exemple si vous l'avez ici)
        # Assurez-vous qu'il n'a pas de marges importantes (mt-0, mb-0)
        ui.button('🏠 ACCUEIL', on_click=lambda: ui.notify('Retour...')) \
            .props('flat color=primary').classes('mb-0')

        if 'game_instance' not in globals():
            global game_instance
            game_instance = AssociationGame()
        
        # 2. Appel du rendu du jeu
        render_ui(game_instance)
