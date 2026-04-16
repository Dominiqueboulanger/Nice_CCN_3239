# css.py - Ce fichier contient uniquement les définitions de style (chaînes de caractères)

STYLE_CSS = '''
    /* Fond de page et typographie */
    body {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
    }

    /* Grille pour les métiers (Etape 1) */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        width: 100%;
        padding: 4px;
    }

    /* La dernière carte prend toute la largeur si elle est seule sur sa ligne */
    .grid-container > *:last-child:nth-child(odd) {
        grid-column: span 2;
    }

    /* --- ANIMATION DU BOUTON ANNEXES --- */
    @keyframes entranceAnim {
        0% { 
            /* Départ de très bas (450px) pour l'effet de surimpression */
            transform: translateY(450px) scale(1.1); 
            opacity: 0;
            filter: blur(4px);
        }
        65% {
            /* Remonte de ~2cm au-dessus de sa place finale (-60px) */
            transform: translateY(-60px) scale(1.05);
            opacity: 1;
            filter: blur(0px);
        }
        85% {
            /* Redressement léger pour stabiliser le rebond */
            transform: translateY(10px) scale(1.02);
        }
        100% { 
            /* Position finale fixe */
            transform: translateY(0) scale(1); 
            opacity: 1;
        }
    }

    .animate-entrance {
        /* Durée de 2.2s pour un mouvement fluide et majestueux */
        animation: entranceAnim 2.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1) !important;
    }

    /* Style des cartes de métier */
    .q-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    /* Effet au clic sur les cartes */
    .q-card:active {
        transform: scale(0.95);
        background-color: #f1f5f9 !important;
        border-color: #3b82f6 !important;
    }

    /* Header avec effet de flou (Glassmorphism) */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 100;
        background-color: rgba(248, 250, 252, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid #e2e8f0;
    }

    /* Barre de recherche (Expansion item) */
    .q-expansion-item {
        background: white;
        border-radius: 16px !important;
        border: 2px solid #1e293b !important;
        overflow: hidden;
    }
'''

# Style réutilisable pour les boutons de texte classiques
BTN_STYLE = "w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-center mb-3 font-medium shadow-sm hover:bg-slate-50"
