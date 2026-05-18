import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "CCN_3239.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_options(column_base, lang, filter_query=""):
    conn = get_connection()
    cursor = conn.cursor()
    column = f"{column_base}_en" if lang == 'EN' else column_base
    query = f"SELECT DISTINCT {column} FROM questions {filter_query} AND {column} IS NOT NULL AND {column} != ''"
    cursor.execute(query)
    options = [r[0] for r in cursor.fetchall()]
    conn.close()
    return options

def fetch_articles_complet(num_racine):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM convention_collective 
        WHERE numero_article_isole = ? 
        OR numero_article_isole LIKE ?
        ORDER BY CAST(numero_article_isole AS INTEGER) ASC
    """, (str(num_racine), str(num_racine) + "-%"))
    results = cursor.fetchall()
    conn.close()
    return results

def get_article_from_question(id_q, col_metier):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {col_metier} FROM questions WHERE id = ?", (id_q,))
    res = cursor.fetchone()
    conn.close()
    return str(res[0]).strip() if res and res[0] else None
def get_db_connection():
    conn = sqlite3.connect('CCN_3239.db')
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn

def get_all_annexes():
    """Récupère la liste simplifiée des annexes pour le menu"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT numero, titre FROM annexes ORDER BY CAST(numero AS INT)")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_annexe_content(numero):
    """Récupère le détail d'une annexe spécifique"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT numero, titre, lien_link, contenu_brut FROM annexes WHERE numero = ?", (str(numero),))
    row = cursor.fetchone()
    conn.close()
    return row
