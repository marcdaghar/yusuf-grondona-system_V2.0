.PHONY: help install test docs clean docker run-demo lint

PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose

help:
	@echo "=== Yusuf-Grondona System — Makefile ==="
	@echo ""
	@echo "  make install     — Installer les dépendances"
	@echo "  make test        — Exécuter les tests unitaires"
	@echo "  make docs        — Générer la documentation"
	@echo "  make run-demo    — Lancer la démonstration complète"
	@echo "  make dashboard   — Lancer le dashboard Streamlit"
	@echo "  make docker      — Démarrer les services Docker"
	@echo "  make clean       — Nettoyer les fichiers temporaires"
	@echo "  make lint        — Vérifier le style du code"

install:
	$(PIP) install -r requirements.txt
	@echo "✅ Dépendances installées"

test:
	pytest tests/ -v --tb=short
	@echo "✅ Tests terminés"

test-coverage:
	pytest tests/ -v --cov=core --cov=simulation --cov=ai --cov-report=html
	@echo "✅ Rapport de couverture généré dans htmlcov/"

docs:
	mkdir -p docs/_build
	sphinx-build -b html docs docs/_build
	@echo "✅ Documentation générée dans docs/_build/"

run-demo:
	$(PYTHON) simulation/run_full.py
	@echo "✅ Démonstration terminée"

dashboard:
	streamlit run dashboard/streamlit_app.py

jupyter:
	jupyter notebook notebooks/

docker:
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Services Docker démarrés"
	@echo "   - Streamlit: http://localhost:8501"
	@echo "   - Jupyter:   http://localhost:8888"

docker-down:
	$(DOCKER_COMPOSE) down
	@echo "✅ Services Docker arrêtés"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf docs/_build/
	rm -rf htmlcov/ .coverage
	rm -rf .pytest_cache/
	@echo "✅ Nettoyage terminé"

lint:
	flake8 core/ simulation/ ai/ governance/ blockchain/ dashboard/ --max-line-length=100
	@echo "✅ Vérification de style terminée"

format:
	black core/ simulation/ ai/ governance/ blockchain/ dashboard/ tests/
	@echo "✅ Formatage terminé"

verify:
	$(PYTHON) -c "import core.grondona_crd; import simulation.yusuf_model; print('✅ Tous les modules importables')"

all: install test docs
	@echo "✅ Installation, tests et documentation terminés"
