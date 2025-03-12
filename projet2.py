import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import pandas as pd
from datetime import datetime
import logging
from retry import retry
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import plotly
import plotly.express as px
import json
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("currency_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clé secrète pour les messages flash

# Configuration du client Google Sheets
def setup_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("currency-tracker-453507-47575d60e456.json", scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de Google Sheets: {e}")
        flash(f"Erreur lors de la configuration de Google Sheets: {str(e)}", "danger")
        raise

# Récupération des taux de change avec retry pour gérer les erreurs temporaires
@retry(tries=3, delay=2, backoff=2)
def get_exchange_rates(base_currency="USD", currencies=None):
    if currencies is None:
        currencies = ["EUR", "GBP", "JPY", "MAD"]
    
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        rates = {}
        for currency in currencies:
            if currency in data["rates"]:
                rates[currency] = data["rates"][currency]
            else:
                logger.warning(f"Devise {currency} non trouvée dans les données API")
        
        return rates, data["time_last_updated"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la récupération des taux de change: {e}")
        flash(f"Erreur lors de la récupération des taux de change: {str(e)}", "danger")
        raise

# Mise à jour du Google Sheet
def update_sheet(sheet, rates, timestamp):
    try:
        # Effacer le contenu existant
        sheet.clear()
        
        # Formater la date pour l'affichage
        date_formatted = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Préparer les données
        headers = ["Devise", "Taux de change", "Date de mise à jour"]
        data = [[currency, rate, date_formatted] for currency, rate in rates.items()]
        
        # Insérer les titres et les données
        sheet.append_row(headers)
        sheet.append_rows(data)
        
        # Formater le tableau
        sheet.format('A1:C1', {'textFormat': {'bold': True}})
        
        # Sauvegarder les données historiques dans un fichier local
        history_file = "currency_history.csv"
        with open(history_file, "a") as f:
            for currency, rate in rates.items():
                f.write(f"{currency},{rate},{date_formatted}\n")
        
        logger.info(f"Mise à jour terminée avec succès: {len(rates)} devises à {date_formatted}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la feuille: {e}")
        flash(f"Erreur lors de la mise à jour de la feuille: {str(e)}", "danger")
        raise

# Routes Flask
@app.route('/')
def index():
    try:
        # Récupérer les données de Google Sheets pour affichage
        client = setup_google_sheets()
        sheet = client.open("Currency Tracker").sheet1
        data = sheet.get_all_records()
        
        # Récupérer la liste des devises disponibles dans l'API
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        available_currencies = list(response.json()["rates"].keys())
        available_currencies.sort()
        
        # Créer un graphique avec Plotly si des données existent
        graph_json = None
        if data:
            df = pd.DataFrame(data)
            if 'Taux de change' in df.columns and 'Devise' in df.columns:
                fig = px.bar(df, x='Devise', y='Taux de change', title='Taux de change par devise')
                graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template('index.html', 
                              data=data, 
                              available_currencies=available_currencies,
                              graph_json=graph_json)
    except Exception as e:
        logger.error(f"Erreur sur la page d'accueil: {e}")
        flash(f"Une erreur s'est produite: {str(e)}", "danger")
        return render_template('index.html', data=[], available_currencies=[])

@app.route('/update', methods=['POST'])
def update():
    try:
        # Récupérer les paramètres du formulaire
        base_currency = request.form.get('base_currency', 'USD')
        selected_currencies = request.form.getlist('currencies')
        
        if not selected_currencies:
            selected_currencies = ["EUR", "GBP", "JPY", "MAD"]
        
        # Récupérer les taux de change
        rates, timestamp = get_exchange_rates(base_currency=base_currency, currencies=selected_currencies)
        
        # Mettre à jour Google Sheets
        client = setup_google_sheets()
        sheet = client.open("Currency Tracker").sheet1
        success = update_sheet(sheet, rates, timestamp)
        
        if success:
            flash(f"Mise à jour réussie de {len(rates)} devises basées sur {base_currency}", "success")
        else:
            flash("La mise à jour a échoué", "danger")
        
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        flash(f"Erreur lors de la mise à jour: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/api/data')
def api_data():
    try:
        client = setup_google_sheets()
        sheet = client.open("Currency Tracker").sheet1
        data = sheet.get_all_records()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Erreur API: {e}")
        return jsonify({"error": str(e)}), 500

# Point d'entrée principal
if __name__ == "__main__":
    # Créer les templates si nécessaire
    os.makedirs('templates', exist_ok=True)
    
    
    # Démarrer l'application Flask
    app.run(debug=True, host='0.0.0.0', port=5000)