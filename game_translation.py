from nicegui import ui
import lexique_manager as lex
import random
import os

# --- SÉCURITÉ RÉSEAU ---
def kill_port(port):
    try:
        os.system(f"lsof -ti:{port} | xargs kill -9 > /dev/null 2>&1")
    except:
        pass

# --- STYLE CSS ADAPTATIF (Identique au test_association) ---
def inject_custom_style():
    ui.add_head_html('''
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
        <style>
            .montserrat { font-family: 'Montserrat', sans-serif !important; }
            .main-container {
                height: 92dvh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .box-card { 
                background-color: white; border-radius: 10px; padding: 6px; 
                cursor: pointer; display: flex; align-items: center; justify-content: center;
                transition: all 0.1s; flex-grow: 1; margin-bottom: 6px; min-height: 0; 
            }
            .box-mot { border: 2px solid #1e3a8a !important; color: #1e3a8a !important; }
            .box-def { border: 2px solid #15803d !important; color: #15803d !important; }
            .responsive-text {
                font-size: clamp(8px, 2.5vw, 11px);
                line-height: 1.2;
                text-align: center;
            }
            .selected-blue { background-color: #dbeafe !important; border-width: 3px !important; }
            .selected-green { background-color: #dcfce7 !important; border-width: 3px !important; }
            .matched { opacity: 0.1 !important; pointer-events: none !important; border-style: dashed !important; }
            
            /* STYLE DES DRAPEAUX XXL */
            .q-btn__content { font-size: 3.5rem !important; }
            .q-btn-group {
                padding: 5px 20px;
                background-color: #f8fafc;
                border-radius: 20px;
                gap: 20px;
            }
        </style>
    ''')

# --- LOGIQUE DU JEU DE TRADUCTION ---
class TranslationGame:
    def __init__(self):
        self.nb_paires = 5 
        self.reset_game()

    def reset_game(self):
        # Utilisation de la nouvelle fonction de lexique_manager
        raw = lex.get_fr_en_pairs(self.nb_paires)
        self.mots_fr = []
        self.mots_en = []
        for item in raw:
            f = str(item['mot_fr']).strip()
            e = str(item['mot_en']).strip()
            self.mots_fr.append({'text': f, 'match': f})
            self.mots_en.append({'text': e, 'match': f})
        
        random.shuffle(self.mots_fr)
        random.shuffle(self.mots_en)
        self.sel_fr = None
        self.sel_en = None
        self.found = set()

    def check(self):
        if self.sel_fr and self.sel_en:
            if self.sel_fr['match'] == self.sel_en['match']:
                ui.notify('Match !', type='positive')
                self.found.add(self.sel_fr['match'])
            else:
                ui.notify('Erreur', type='negative')
            self.sel_fr = None
            self.sel_en = None
            render_ui.refresh()

# --- INTERFACE UTILISATEUR ---
@ui.refreshable
def render_ui(game):
    with ui.column().classes('w-full max-w-md mx-auto p-2 montserrat main-container'):
        
        # Titre (les drapeaux ne sont ici que décoratifs ou informatifs)
        #with ui.row().classes('w-full justify-center items-center mb-4'):
             #ui.label("🇫🇷 ↔ 🇬🇧").classes('text-5xl py-2')

        ui.label("Associez les traductions").classes('text-xl font-black text-center w-full mb-2')
        
        with ui.row().classes('w-full no-wrap gap-2 flex-grow items-stretch'):
            # Colonne FRANÇAIS (Même CSS que "MOTS")
            with ui.column().classes('w-1/2 gap-0 items-stretch'):
                ui.label("FRANÇAIS").classes('text-[9px] font-black opacity-40 mb-1')
                for m in game.mots_fr:
                    is_done = m['match'] in game.found
                    active = game.sel_fr == m
                    card = ui.card().classes('box-card box-mot shadow-none')
                    if is_done: card.classes('matched')
                    if active: card.classes('selected-blue')
                    with card:
                        ui.label(m['text']).classes('responsive-text font-bold')
                    card.on('click', lambda m=m: (setattr(game, 'sel_fr', m), game.check(), render_ui.refresh()))

            # Colonne ANGLAIS (Même CSS que "DÉFINITIONS")
            with ui.column().classes('w-1/2 gap-0 items-stretch'):
                ui.label("ENGLISH").classes('text-[9px] font-black opacity-40 mb-1')
                for e in game.mots_en:
                    is_done = e['match'] in game.found
                    active = game.sel_en == e
                    card = ui.card().classes('box-card box-def shadow-none')
                    if is_done: card.classes('matched')
                    if active: card.classes('selected-green')
                    with card:
                        ui.label(e['text']).classes('responsive-text font-bold')
                    card.on('click', lambda e=e: (setattr(game, 'sel_en', e), game.check(), render_ui.refresh()))

        if len(game.found) == game.nb_paires:
            ui.button("REJOUER", on_click=lambda: (game.reset_game(), render_ui.refresh())) \
                .classes('w-full py-3 bg-blue-900 text-white rounded-xl font-bold mt-2 shadow-lg')

@ui.page('/')
def main():
    inject_custom_style()
    if 'game_instance_trad' not in globals():
        global game_instance_trad
        game_instance_trad = TranslationGame()
    render_ui(game_instance_trad)

