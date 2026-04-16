# css.py

STYLE_CSS = '''
    /* --- CONFIGURATION DE BASE --- */
    body {
        background-color: #f8fafc;
        font-family: sans-serif;
        margin: 0;
        padding: 0;
    }

    /* --- ZOOM SÉCURISÉ POUR LES CLICS --- */
    .zoom-page {
        transform: scale(0.92);
        transform-origin: top center;
        width: 108.7% !important; /* Compense le scale pour les clics */
        margin-left: -4.35%;       /* Recentrage manuel */
        pointer-events: auto !important;
    }

    /* --- ANIMATION --- */
    @keyframes entranceAnim {
        0% { transform: translateY(200px); opacity: 0; }
        60% { transform: translateY(-40px); opacity: 1; }
        100% { transform: translateY(0); opacity: 1; }
    }

    .animate-entrance {
        animation: entranceAnim 2s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        background-color: #1e293b !important;
        color: white !important;
    }

    /* --- GRILLE ET CARTES --- */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        width: 100%;
        padding: 12px;
    }

    .q-card {
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
        cursor: pointer !important;
    }

    /* --- FIX DU HEADER (Verrouillage 1 ligne) --- */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: rgba(248, 250, 252, 0.9);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-bottom: 1px solid #e2e8f0;
        width: 100%;
        /* Empêche le contenu de déborder ou de créer une 2ème ligne */
        overflow: hidden; 
    }

    /* Force le conteneur flex à ne pas wrapper */
    .header-row {
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100%;
    }
'''

BTN_STYLE = "w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-center mb-3 font-medium shadow-sm"
