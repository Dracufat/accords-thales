# Projet Documentation

## Structure
- fichiers .md répartis dans 4 sous-dossiers  correspondant a des types d'accord (les .md a la racine ne sont pas de la meme nature)
  - docs/las-rungis-toulouse: Etablissement LAS Rungis - Toulouse
  - docs/las-fr: Société LAS France
  - docs/accords-groupe: Groupe
  - docs/accords-interprofessionnels: Accords Interprofessionnels
- fichiers .pdf source correspondant a chaque .md dans le dossier source/ attenant
- Un sommaire (SOMMAIRE.md) à la racine
- Objectif : générer un site MkDocs Material avec recherche plein texte

## Stack
- MkDocs avec le thème Material
- Déploiement prévu sur  GitHub Pages
- Langue : français

## Conventions
- Ne pas modifier le contenu des fichiers .md existants dans les sous dossiers
- Demander avant toute modification des sommaires SOMMMAIRE.md présents dans chaque catégorie
- Conserver l'arborescence actuelle des 4 sous-dossiers
- Le fichier sommaire à la racine sert de base pour la navigation mkdocs.yml

## Conventions sur les fichierss markown des accords

- dans le fichier md juste apres le titre doit apparaitre un lien pour télécharger l'accord dans un bloc de citation
- dans le fichier md juste apres le lien pour le téléchargement le bloc 

> 📅 Signé le **__date-de-signature__** — __lieu-de-signature__
>
> 🏢 **Thales** : CFDT: Guy HENRY
>
> ✅ **Signataires** : CFDT (Guy HENRY) · CFE-CGC (Hervé TAUSKY) · CFTC (Alain DESVIGNES) · FO (Dominique ALLO)
>
> ❌ **Non Signataires** : __liste-des-orgas-non-signataires__


## Procédure pour l'ajout d'un accord

- si je te signale qu'un accord a été ajouté, j'ai créé un fichier .md a partir d'un nouveau pdf que tu peux identifier car il n'a pas été commité
- rajoute dans le fichier md juste apres le titre un lien pour télécharger l'accord: 
`>[Télécharger le PDF](sources/<nom-de-l-accord.pdf)`
- rajoute une ligne le référencant dans le sommaire du type 