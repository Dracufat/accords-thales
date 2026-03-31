# Accords Thales

Extraction et traitement des accords groupe Thales à partir de fichiers PDF en utilisant [marker-pdf](https://github.com/VikParuchuri/marker).

Publication des accords sur le site [Pages](https://dracufat.github.io/accords-thales/)

## Prérequis

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) ou [Anaconda](https://www.anaconda.com/)

## Installation

### 1. Créer l'environnement conda

```bash
conda create -n accords-thales python=3.12 -y
conda activate accords-thales
```

> **Note :** Python 3.12 est requis. marker-pdf utilise `aiohttp` qui dépend du module `cgi` supprimé en Python 3.13.

### 2. Installer les dépendances

```bash
pip install marker-pdf
```

### 3. Vérifier l'installation

```bash
python -c "from marker.converters.pdf import PdfConverter; print('marker-pdf installé avec succès')"
```

## Utilisation

```bash
conda activate accords-thales
python main.py
```
### Test avec marker

```bash
marker_single accords-groupe/sources/groupe-1993-11-16-accord-sur-la-creation-dun-comite-europeen-thomson-csf-et-filiales.pdf --output_dir ./accords-groupe --force_ocr 
```

## Documentation (MkDocs)

### Installer MkDocs Material

```bash
pip install mkdocs-material
```

### Lancer le serveur de développement

```bash
mkdocs serve
```

Le site est disponible sur http://127.0.0.1:8000/

### Générer le site statique

```bash
mkdocs build
```

Le site est généré dans le dossier `site/`. Permet de verifier les erreurs. Ne 

## Structure du projet

```
accords-thales/
├── docs/
│    ├── /accords-groupe    # accords en format MD
│    │   ├── /sources       # sources en pdf
│    │   ├── SOMMAIRE.md    # liste des  accords en cours
│    │   └── REVOLU.md      # liste des accords révolus. ils ne sont pas ajoutés dans la nav
│    ├── /accords-interprofessionnels
│    │    └── /sources
│    ├── ...
│ 
├── site/  # contient le site statique
├── main.py
└── README.md
```

### Pour ajouter un accord

1. ajouter le fichier pdf OCRisé au bon endroit (choisir la sous catégorie correcte)
2. générer le fichier md, par exemple avec Claude
3. mettre à jour le fichier SOMMAIRE.md de la sous-catégorie
4. Exécuter le script `update_index_and_mkdocs.py`
5. Commit and push, le workflow github publiera la nouvelle version du site 


### Pour supprimer un accord révolu

1. supprimer la reference dans le fichier SOMMAIRE.md de la sous-catégorie
2. Renommer le fichier .md correspodant en préfixant par révolu
3. ajouter la reference dans le fichier REVOLUS.md
4. Exécuter le script `update_index_and_mkdocs.py`
5. Commit and push, le workflow github publiera la nouvelle version du site 