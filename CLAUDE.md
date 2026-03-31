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
- Le fichier sommaire contient un bloc de citation avec le nombre de documents et la date de derniere modification

## Conventions sur les fichiers markown des accords

- dans le fichier md juste apres le titre doit apparaitre un bloc de citation avec le lien pour télécharger l'accord : `>[Télécharger le PDF](sources/<nom-de-l-accord.pdf)`
- dans le fichier md juste apres le lien de teléchargement doit apparaitre un bloc de citation decrivant la signature. Les informations nécessaires a la completion des placeholders se trouve usuellement dans la derniere section avant les annexes. Le template du bloc est le suivant:
\> 📅 Signé le **__date-de-signature__** — __lieu-de-signature__
\>
\> 🏢 **Thales** : __Nom-du-signataire-de-la direction__, __fonction__
\>
\> ✅ **Signataires** : __orga1__ (__signataire1__) · __orga2__ (__signataire2__) · ...
\>
\> ❌ **Non Signataires** : __liste-des-orgas-non-signataires__
- dans le fichier md juste apres le bloc de signature doit apparaitre un autre bloc de citation décrivant la durée de validité de l'accord. Les informations nécessaires a la completion des placeholders se trouve usuellement dans les dernieres section avant les annexes. Le template du bloc est le suivant:
\> 📅 Conditions de validité: jusqu'à  **__date-de-validité__** 
- dans le fichier md juste apres le bloc de validié doit apparaitre un autre bloc de citation listant les éléments liés (avenants, accord auquel l'avenant est lié). Le template du bloc est le suivant:
\> Elements liés:
\>- [__accord___(__date__)](lien_vers_le_md)
\>- [__avenant___(__date__)](lien_vers_le_md)
\>- [__annexe___(__date__)](lien_vers_le_md)



- il ne doit pas y avoir de sommaire dans le fichier md

## Procédure pour l'ajout d'un accord

- si je te signale qu'un accord a été ajouté, j'ai créé un fichier .md à partir d'un nouveau pdf que tu peux identifier car il n'a pas été commité
- rajoute dans le fichier md le bloc de téléchargement
- rajoute dans le fichier md le bloc de signature
- rajoute une ligne le référencant dans le sommaire du type en te basant sur la totalité en l'inserant dans les lignes existantes
- met a jour le bloc de citation du sommaire

