#!/bin/bash
# deploy.sh — Déploiement des smart contracts
# Author: Marc Daghar, CC BY-SA 4.0

set -e

NETWORK=${1:-local}
echo "🔧 Déploiement sur le réseau : $NETWORK"

cd contracts

if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

echo "🔨 Compilation..."
npx hardhat compile

echo "🚀 Déploiement..."
npx hardhat run scripts/deploy.js --network $NETWORK

echo "✅ Déploiement terminé"
