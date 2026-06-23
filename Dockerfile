FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Commande par défaut
CMD ["streamlit", "run", "dashboard/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
