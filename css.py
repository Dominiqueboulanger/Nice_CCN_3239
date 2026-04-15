# --- STYLES GÉNÉRAUX (Injection HTML/CSS) ---
STYLE_CSS = '''
    body { overflow-x: hidden; background-color: #f8fafc; }
    .sticky-header { 
        position: sticky; top: 0; z-index: 1000; 
        background: white; border-bottom: 2px solid #3b82f6; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        width: 100%;
        padding: 8px;
    }
    .full-width-btn { grid-column: span 2; }
    .article-card {
        border-left: 5px solid #3b82f6;
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        padding: 20px;
    }
'''

# --- STYLES TAILWIND (Variables Python) ---

# Le style de tes boutons d'accueil (Grille)
BTN_STYLE = (
    'w-full h-28 bg-white text-black border-2 border-slate-300 '
    'rounded-2xl shadow-md text-sm font-bold hover:bg-blue-50 '
    'px-3 whitespace-pre-line'
)

# Style pour les cartes de la liste des annexes
CARD_ANNEXE = (
    "w-full p-4 cursor-pointer hover:bg-blue-50 "
    "border-l-4 border-blue-500 shadow-sm transition-all"
)

# Style pour le texte des annexes 1 à 4 (Lecture fluide)
TEXT_ANNEXE = (
    "text-base leading-relaxed text-slate-800 "
    "text-justify font-sans"
)

# Style pour les tableaux des annexes 5 à 7 (Grilles de salaires)
TEXT_TABLEAU = (
    "text-[10px] font-mono whitespace-pre-wrap "
    "text-slate-700 leading-tight"
)

# Zone de défilement (Scroll Area)
SCROLL_AREA = "w-full h-[70vh] border-y bg-white p-4"
