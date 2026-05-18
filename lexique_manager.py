import sqlite3
import os

# --- CONFIGURATION ---
DB_NAME = "CCN_3239.db"

def get_db_connection():
    """Gère la connexion sécurisée et le chemin de la base."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, DB_NAME)
    
    if not os.path.exists(db_path):
        print(f"Erreur : La base est introuvable ici : {db_path}")
        return None
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"Erreur de connexion SQLite : {e}")
        return None

def get_random_lexicon_pair(n, lang='FR'):
    """
    MODE QUIZ : Récupère n paires (mot, définition) pour une langue donnée.
    Utilisé pour le jeu 'Mot <-> Définition'.
    """
    conn = get_db_connection()
    if not conn: return []

    try:
        cursor = conn.cursor()
        # Sélection dynamique des colonnes selon la langue
        col_mot = "mot_fr" if lang == 'FR' else "mot_en"
        col_def = "def_fr" if lang == 'FR' else "def_en"

        query = f"""
            SELECT {col_mot} AS mot, {col_def} AS def 
            FROM lexique 
            WHERE {col_mot} IS NOT NULL AND {col_mot} != ''
            ORDER BY RANDOM() 
            LIMIT ?
        """
        
        cursor.execute(query, (n,))
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"Erreur dans get_random_lexicon_pair : {e}")
        return []

def get_fr_en_pairs(n):
    """
    MODE TRADUCTION : Récupère n paires (mot_fr, mot_en).
    Utilisé pour le nouveau jeu 'Français <-> Anglais'.
    """
    conn = get_db_connection()
    if not conn: return []

    try:
        cursor = conn.cursor()
        # On sélectionne les deux colonnes de mots
        query = """
            SELECT mot_fr, mot_en 
            FROM lexique 
            WHERE mot_fr IS NOT NULL AND mot_en IS NOT NULL 
              AND mot_fr != '' AND mot_en != ''
            ORDER BY RANDOM() 
            LIMIT ?
        """
        
        cursor.execute(query, (n,))
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"Erreur dans get_fr_en_pairs : {e}")
        return []
