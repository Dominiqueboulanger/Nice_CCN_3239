# css.py

STYLE_CSS = '''
    /* --- RESET & ZOOM --- */
    .zoom-page {
        transform: scale(0.92);
        transform-origin: top center;
        width: 100%;
    }

    /* --- L'ANIMATION --- */
    @keyframes entranceAnim {
        0% { 
            transform: translateY(300px); 
            opacity: 0;
        }
        60% {
            /* On monte de 100px */
            transform: translateY(-100px);
            opacity: 1;
        }
        100% { 
            /* On revient à 0 (sa place) */
            transform: translateY(0);
            opacity: 1;
        }
    }

    .animate-entrance {
        animation: entranceAnim 2.5s ease-out forwards !important;
        background-color: #1e293b !important;
        color: white !important;
    }

    /* --- GRILLE --- */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        width: 100%;
    }

    .q-card {
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
    }

    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: rgba(248, 250, 252, 0.9);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #e2e8f0;
    }
'''

BTN_STYLE = "w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-center mb-3 font-medium shadow-sm"
