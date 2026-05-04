# 📘 Guide de la Convention Collective Nationale (CCN) 3239

Application web interactive développée avec **NiceGUI** permettant de naviguer dans les articles et annexes de la CCN 3239, optimisée pour le mobile et déployée sur **Clever Cloud**.

## 🚀 Structure du Projet

*   **`main.py`** : Point d'entrée de l'application (Moteur `build_ui` et gestion des étapes).
*   **`sql_manager.py`** : Gestion des requêtes SQL vers la base `CCN_3239.db`[cite: 1].
*   **`css.py`** : Centralisation des styles et du design "App Native"[cite: 1, 2].
*   **`/static`** : Dossier contenant les images et les PDF des annexes[cite: 1].

## 🛠️ Fonctionnalités Clés

*   **Navigation Guidée** : Parcours par métier (Assistant Maternel, Employé Familial, etc.)[cite: 1].
*   **Recherche Directe** : Accès rapide à un article par son numéro[cite: 1].
*   **Multilingue** : Support complet FR / EN commutable instantanément[cite: 1].
*   **Interactivité** : Détection automatique et chargement dynamique des articles cités[cite: 1].

## ☁️ Déploiement (Clever Cloud)

L'application est configurée pour être déployée automatiquement via GitHub :
1.  **Port** : Utilise la variable d'environnement `PORT` fournie par le serveur[cite: 1].
2.  **Stabilité** : Script JS intégré pour la reconnexion automatique sur smartphone[cite: 1].
3.  **Lancement** : Exécuter `python main.py`[cite: 1].

## 🔒 Maintenance
*   **État Utilisateur** : Géré via la classe `AppState` et un `storage_secret` sécurisé[cite: 1].
*   **Base de données** : SQLite avec gestion des timeouts pour éviter les conflits[cite: 1].
