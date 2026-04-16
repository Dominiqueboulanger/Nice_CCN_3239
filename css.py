# css.py - Version "Mouvement Fluide"

STYLE_CSS = '''
    /* --- CONFIGURATION GLOBALE --- */
    body {
        background-color: #f8fafc;
        font-family: -apple-system, system-ui, sans-serif;
        overflow-x: hidden;
    }

    /* --- LE ZOOM ARRIÈRE (Pour la visibilité) --- */
    .zoom-page {
        transform: scale(0.92);
        transform-origin: top center;
        width: 100%;
    }

    /* --- L'ANIMATION DU BOUTON (Réglages Calmes) --- */
    @keyframes entranceAnim {
        0% { 
            transform: translateY(300px) scale(0.9); 
            opacity: 0;
            top: 0px;
        }
        50% {
            /* MONTÉE : Seulement 80px vers le haut pour rester élégant */
            top: -80px !important; 
            opacity: 1;
            transform: scale(1.03) !important;
        }
        100% { 
            /* POSITION FINALE : Retour parfait à sa place */
            top: 0px !important;
            transform: translateY(0) scale(1) !important; 
            opacity: 1;
        }
    }

    .animate-entrance {
        position: relative !important;
        z-index: 999 !important;
        display: block !important;
        /* 3 secondes pour un mouvement très fluide et "premium" */
        animation: entranceAnim 3.0s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        background-color: #1e293b !important; /* Couleur Slate-800 */
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.2) !important;
    }

    /* --- GRILLE ET CARTES --- */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        width: 100%;
    }

    .q-card {
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
        transition: transform 0.2s;
    }

    .q-card:active {
        transform: scale(0.95);
    }

    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: rgba(248, 250, 252, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid #e2e8f0;
    }
'''

BTN_STYLE = "w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-center mb-3 font-medium shadow-sm"
