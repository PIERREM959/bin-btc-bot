# BIN/BTC Bot 🤖

Bot de trading automatique sur BTCUSDT en UT 1H avec stratégie simple :

- Achat si la bougie actuelle clôture au-dessus des 3 précédentes.
- Vente automatique si perte >10% depuis le plus haut atteint.

## Démarrage

1. Créer un fichier `.env` basé sur `.env.example`
2. Installer les dépendances :
```bash
pip install -r requirements.txt
