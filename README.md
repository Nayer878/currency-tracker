# Currency Tracker

## Description
Ce projet est une application Flask qui permet de suivre les taux de change en temps réel et de les enregistrer dans un Google Sheets. Les données historiques sont également sauvegardées dans un fichier local `currency_history.csv`.

## Fonctionnalités
- Récupération des taux de change via une API externe
- Mise à jour d'un Google Sheets avec les taux de change
- Sauvegarde des données historiques dans un fichier CSV
- Interface utilisateur pour visualiser les données et mettre à jour les taux

## Installation
1. Cloner le dépôt
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Configurer les clés d'API dans le fichier `.env`
4. Lancer l'application :
   ```bash
   python projet2.py
   ```

## Utilisation
- Accéder à l'interface utilisateur à l'adresse `http://localhost:5000`
- Mettre à jour les taux de change via le bouton "Mettre à jour les taux"

## Tests
Pour exécuter les tests unitaires :
```bash
python test_projet2.py
```

## Technologies utilisées
- Flask
- API pour les taux de change (https://www.exchangerate-api.com/)
- Google Sheets API
- CSV pour le stockage local

## Auteur
Nael
