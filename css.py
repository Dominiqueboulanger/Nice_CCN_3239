# css.py - Version Interaction & Zoom Corrigée

STYLE_CSS = '''
    /* --- 1. CONFIGURATION DE BASE --- */
    body {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1e293b;
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }

    /* --- 2. SOLUTION DE ZOOM (Boutons cliquables) --- */
    .zoom-page {
        transform: scale(0.92);
        transform-origin: top center;
        /* Compensation mathématique pour que la zone de clic soit alignée */
        width: 108.7% !important; 
        margin-left: -4.35%;
        pointer-events: auto !important;
    }

    /* Force NiceGUI à ne pas masquer les débordements d'animation */
    .nicegui-content, .q-page {
        overflow: visible !important;
    }

    /* --- 3. L'ANIMATION DU BOUTON --- */
    @keyframes entranceAnim {
        0% { 
            transform: translateY(300px); 
            opacity: 0;
        }
        60% {
            /* Montée élégante */
            transform: translateY(-60px); 
            opacity: 1;
        }
        100% { 
            /* Retour exact à sa position de clic */
            transform: translateY(0); 
            opacity: 1;
        }
    }

    .animate-entrance {
        position: relative !important;
        z-index: 10 !important;
        animation: entranceAnim 2.5s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        background-color: #1e293b !important;
        color: white !important;
        pointer-events: auto !important;
    }

    /* --- 4. GRILLE ET CARTES --- */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        width: 100%;
        padding: 10px;
    }

    .grid-container > *:last-child:nth-child(odd) {
        grid-column: span 2;
    }

    .q-card {
        transition: transform 0.1s ease-in-out;
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
        cursor: pointer !important;
    }

    .q-card:active {
        transform: scale(0.96) !important;
    }

    /* --- 5. HEADER --- */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: rgba(248, 250, 252, 0.9);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid #e2e8f0;
    }
'''

# Style pour les boutons des étapes internes
BTN_STYLE = "w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-center mb-3 font-medium shadow-sm"
