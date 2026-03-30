#!/bin/bash

OUTPUT_DIR=".."

for pdf in \
"groupe-2012-avenant-n1-a-laccord-cadre-groupe-relatif-a-legalite-professionnelle-entre-les-femmes-et-les-hommes-dans-le-groupe-thales-en-france.pdf" \
"groupe-2012-avenant-n2-a-laccord-portant-reglement-du-plan-depargne-pour-la-retraite-collectif-du-groupe-thales-perco.pdf" \
"groupe-2016-01-15-avenant-n1-a-laccord-sur-le-comite-de-groupe-thales-du-14-novembre-2011.pdf" \
"groupe-2016-05-20-avenant-n2-a-laccord-de-participation-des-salaries-aux-resultats-du-groupe-thales.pdf" \
"groupe-2016-05-20-avenant-n3-a-laccord-portant-reglement-du-plan-depargne-pour-la-retraite-collectif-du-groupe-thales-perco.pdf" \
"groupe-2018-06-29-avenant-n3-a-laccord-de-participation-des-salaries-aux-resultats-des-societes-du-groupe-thales.pdf" \
"groupe-2018-avenant-n4-a-laccord-portant-reglement-du-plan-depargne-pour-la-retraite-collectif-du-groupe-thales-perco.pdf" \
"groupe-2019-04-19-statuts-association-thales-des-retraites-du-regime-dependance-at2rd.pdf" \
"groupe-2022-01-17-avenant-n1-a-laccord-groupe-relatif-aux-garanties-frais-de-sante-et-prevoyance-du-groupe-thales.pdf" \
"groupe-2022-01-17-avenant-n1-a-laccord-instituant-un-regime-surcomplementaire-obligatoire-aux-garanties-collectives-frais-de-sante-du-groupe-thales.pdf" \
"groupe-2022-01-27-avenant-n1-a-laccord-groupe-sur-la-composition-et-le-fonctionnement-du-comite-interentreprise-du-groupe-thales.pdf" \
"groupe-2022-01-27-avenant-n5-constatant-la-possibilite-de-poursuivre-lapplication-de-laccord-de-participation-des-salaries-aux-resultats-des-societes-du-groupe-thales.pdf" \
"groupe-2022-10-03-avenant-n1-a-laccord-groupe-portant-transformation-du-perco-en-plan-depargne-retraite-collectif-pereco-et-reglement-dudit-pereco.pdf" \
"groupe-2022-10-03-avenant-n1-a-laccord-groupe-sur-les-deplacements-professionnels.pdf" \
"groupe-2022-10-03-avenant-n6-a-laccord-de-participation-des-salaries-aux-resultats-des-societes-du-groupe-thales.pdf" \
"groupe-2022-10-avenant-n2-a-laccord-groupe-portant-sur-la-mise-en-place-dun-regime-surcomplementaire-obligatoire-aux-garanties-collectives-frais-de-sante.pdf" \
"groupe-2022-12-20-avenant-n3-a-laccord-groupe-relatif-aux-garanties-frais-de-sante-et-prevoyance-du-groupe-thales.pdf" \
"groupe-2023-01-16-avenant-n4-a-laccord-groupe-relatif-aux-garanties-frais-de-sante-et-prevoyance-du-groupe-thales.pdf" \
"groupe-2023-04-27-avenant-n2-a-laccord-groupe-portant-transformation-du-perco-en-plan-depargne-retraite-collectif-pereco-et-reglement-dudit-pereco.pdf" \
"groupe-2023-06-20-avenant-n7-a-laccord-de-participation-des-salaries-aux-resultats-des-societes-du-groupe-thales.pdf" \
"groupe-2023-12-avenant-a-laccord-groupe-en-faveur-des-personnes-en-situation-de-handicap-annees-2021-2022-2023.pdf" \
"groupe-2024-03-20-avenant-n1-a-laccord-groupe-visant-a-favoriser-le-developpement-professionnel-et-lemploi-par-des-demarches-danticipation.pdf" \
"groupe-2024-03-20-avenant-n3-a-laccord-groupe-portant-transformation-du-perco-en-plan-depargne-retraite-collectif-pereco-et-reglement-dudit-pereco.pdf" \
"groupe-2024-04-avenant-n2-a-laccord-groupe-sur-les-deplacements-professionnels.pdf" \
"groupe-2024-07-26-avenant-n2-a-laccord-groupe-en-faveur-des-personnes-en-situation-de-handicap-annees-2021-2022-2023.pdf" \
"groupe-2024-10-03-avenant-n4-a-laccord-groupe-portant-transformation-du-perco-en-plan-depargne-retraite-collectif-pereco-et-reglement-dudit-pereco.pdf" \
"groupe-2025-04-23-avenant-n2-a-laccord-groupe-visant-a-favoriser-le-developpement-professionnel-et-lemploi-par-des-demarches-danticipation.pdf"

do
  echo "=== $(basename "$pdf") ==="
  marker_single "$pdf" --output_dir "$OUTPUT_DIR" --force_ocr  \
    && echo "  OK" \
    || echo "  ERREUR"
done