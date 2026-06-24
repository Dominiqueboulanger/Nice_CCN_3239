# Guide CCN 3239 — Application Web Mobile-First

Une application web interactive et responsive conçue avec NiceGUI (Python) pour explorer la Convention Collective Nationale (CCN) 3239 (Particulier employeur et emploi à domicile).

---

## 🛠️ Fonctionnalités de l'Application

- Navigation par Profil Métier : Redirection et filtrage automatique selon le profil sélectionné (Assistant Maternel, Employé Familial, Assistant de Vie, etc.).
- Recherche Directe : Accès instantané à un article spécifique de la CCN via une boîte de dialogue dédiée.
- Double Niveau de Lecture (Bilingue) : Commutation dynamique (FR/EN) entre le résumé pédagogique/simplifié et le texte officiel intégral de la convention.
- Mise en Évidence Légale : Repérage visuel et coloration automatique en rouge des mentions liées aux modifications de l'Avenant n° 10 du 9 septembre 2025 (Rupture pour inaptitude).
- Espace Annexes : Consultation des résumés d'annexes et téléchargement des documents officiels stockés en PDF.
- Espace Ludique : Deux mini-jeux éducatifs intégrés (Lexique ↔ Définitions et Glossaire Français ↔ Anglais).
- Statistiques & Analytics : Suivi de la navigation des utilisateurs via Google Tag Manager (`gtag` / Écrans applicatifs).

---

## 💾 Exploitation de la Base de Données (`CCN_3239.db`)

L'application s'appuie sur une base de données SQLite3 structurée autour des tables suivantes :

1. `convention_collective` : Contient le corps des articles.
   - Requêtes basées sur le champ `numero_article_isole`.
   - Extraction conditionnelle selon la langue de la colonne `texte_simplifie` (FR) ou `texte_simplifie_en` (EN).
   - Accès au champ `texte_integral` au format Markdown pour l'affichage officiel.
2. `liens_inter_articles` : Gère le maillage et les relations de dépendance entre articles (`source` ↔ `cible`) pour suggérer des boutons de navigation connexes.
3. `annexes` : Stocke le catalogue des annexes (`numero`, `titre`, `resume_fr`, `resume_en`).
4. `questions` : Utilisée lors des étapes de filtrage pour associer les parcours utilisateurs (`etape_vie`, `famille`, `theme`) aux articles cibles correspondants (`colonne_metier`).

---
