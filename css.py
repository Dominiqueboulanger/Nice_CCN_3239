# css.py

STYLE_CSS = '''
    /* --- CONFIGURATION GÉNÉRALE --- */
    body { background-color: #f8fafc; font-family: sans-serif; margin: 0; padding: 0; }

    /* --- ACCUEIL COMPACT (Mobile) --- */
    .grid-container {
        display: grid; grid-template-columns: repeat(2, 1fr);
        gap: 15px; /* Augmenté de 10 à 15 pour plus d'espace blanc */
        width: 100%; padding: 8px 12px;
    }
    .q-card {
        border: 2px solid #e2e8f0; border-radius: 20px !important;
        height: 115px !important; /* Augmenté pour laisser de la place au texte plus grand */
        display: flex; flex-direction: column;
        
        /* CENTRAGE TOTAL */
        justify-content: center; 
        align-items: center; 
        text-align: center;
        
        padding: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    /* TAILLE DES CARACTÈRES DANS LES CARTES */
    .q-card label { 
        font-size: 14px !important; /* Augmenté de 11px à 14px */
        line-height: 1.2 !important; 
        font-weight: 700 !important; /* Plus épais pour la lisibilité */
    }
    
    .q-card i { 
        font-size: 1.6rem !important; /* Icône légèrement plus grande */
        margin-bottom: 6px !important; 
    }
    
    /* Force l'aspect cliquable */
    .grid-container .q-card {
        cursor: pointer;
        transition: transform 0.1s, background-color 0.1s;
    }
    
    .grid-container .q-card:active {
        background-color: #f1f5f9 !important;
        transform: scale(0.96);
    }
    
    /* Style spécifique pour le label "ARTICLE CCN 1 CLIC" */
    .special-label {
        font-size: 11px !important;
        font-weight: 900 !important;
        color: #065f46 !important;
    }

    /* --- HEADER --- */
    .sticky-header {
        position: sticky; top: 0; z-index: 1000;
        background-color: rgba(248, 250, 252, 0.95);
        backdrop-filter: blur(8px); border-bottom: 1px solid #e2e8f0;
        width: 100%; height: 44px; overflow: hidden; 
    }
    .header-row {
        display: flex !important; align-items: center !important;
        justify-content: space-between !important; width: 100%; height: 100%;
        padding: 0 12px !important;
    }

    /* --- ANNEXES ET CONTENU --- */
    .annexe-container {
        display: flex; flex-direction: column; width: 100%;
        max-width: 700px; margin: 0 auto; padding: 20px; gap: 20px;
    }
    .annexe-card-info {
        background: white; border-radius: 24px; padding: 25px;
        border: 2px solid #e2e8f0; border-top: 6px solid #1e3a8a;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center; /* Centrage du texte dans les annexes */
    }
'''

# --- STYLE DES BOUTONS (Étapes Situation/Famille/Questions) ---
# Changé text-lg pour une taille bien visible et font-black pour le gras
BTN_STYLE = "w-full h-auto py-4 bg-white text-black border-2 border-slate-200 rounded-xl px-4 text-center mb-5 font-black shadow-sm uppercase text-lg leading-tight"
