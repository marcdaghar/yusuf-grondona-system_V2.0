#!/bin/bash
# generate_docs.sh — Génération de la documentation
# Author: Marc Daghar, CC BY-SA 4.0

set -e

echo "📚 Génération de la documentation..."

mkdir -p docs/_build

# Générer la documentation Sphinx
sphinx-build -b html docs docs/_build

# Générer le PDF de l'article (si pandoc disponible)
if command -v pandoc &> /dev/null; then
    echo "📄 Génération du PDF de l'article..."
    pandoc docs/CBU-X_v2.0_Article.md -o docs/CBU-X_v2.0_Article.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --toc \
        -N
    echo "✅ PDF généré: docs/CBU-X_v2.0_Article.pdf"
fi

echo "✅ Documentation générée dans docs/_build/"
