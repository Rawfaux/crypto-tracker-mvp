from flask import render_template, request, redirect, url_for, Blueprint
import requests
from datetime import datetime
from .models import db, Transaction  # Der Punkt bedeutet: aus dem aktuellen Ordner (crypto_tracker)
from .config import COIN_MAPPING, API_URL # Wird im nächsten Schritt benötigt

# Erstelle einen "Bauplan" für unsere Routen
# Dadurch weiß Flask, dass diese Routen zur Hauptanwendung gehören
tracker_blueprint = Blueprint('tracker', __name__)


# --- Funktion zum Abrufen der Preise (Hilfsfunktion) ---
def get_current_prices():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {}


# --- Haupt-Route (GET-Request zur Anzeige des Portfolios) ---
@tracker_blueprint.route("/")
def show_portfolio():
    # Sortiere die Transaktionen absteigend nach Datum (neueste zuerst)
    transactions = Transaction.query.order_by(Transaction.date_bought.desc()).all() 
    current_prices = get_current_prices()
    
    # Berechnungen für das Template
    total_current_value = 0
    total_invested = 0
    
    # Ergänze jede Transaktion um aktuelle Werte (P/L)
    transactions_with_data = []
    
    for tx in transactions:
        symbol = tx.symbol.upper()
        coin_key = COIN_MAPPING.get(symbol)
        
        current_price = tx.price_usd 
        
        if coin_key and coin_key in current_prices:
            current_price = current_prices[coin_key]['usd']
            
        invested = tx.amount * tx.price_usd
        current_value = tx.amount * current_price
        profit_loss = current_value - invested
        
        total_current_value += current_value
        total_invested += invested
        
        # Erstelle ein Dictionary für die verbesserte Ausgabe im Template
        transactions_with_data.append({
            'symbol': symbol,
            'amount': tx.amount,
            'price_usd': tx.price_usd,
            'date_bought': tx.date_bought,
            'current_value': current_value,
            'profit_loss': profit_loss
        })

    total_p_l = total_current_value - total_invested
    
    return render_template(
        'portfolio.html',
        transactions=transactions_with_data,
        total_invested=total_invested,
        total_current_value=total_current_value,
        total_p_l=total_p_l,
        message=request.args.get('message'), 
        message_type=request.args.get('message_type', 'success')
    )


# --- Route zum Hinzufügen einer Transaktion (POST-Request vom Formular) ---
@tracker_blueprint.route("/add_transaction", methods=['POST'])
def add_transaction():
    symbol = request.form['symbol'].upper()
    
    # 1. Validierung der numerischen Eingaben (Typ-Prüfung)
    try:
        amount = float(request.form['amount'])
        price_usd = float(request.form['price_usd'])
    except ValueError:
        return redirect(url_for('tracker.show_portfolio', 
                                message='Fehler: Menge und Preis müssen gültige Zahlen sein.', 
                                message_type='error'))
        
    # 2. Validierung der logischen Eingaben (Werte-Prüfung)
    if amount <= 0 or price_usd <= 0:
        return redirect(url_for('tracker.show_portfolio', 
                                message='Fehler: Menge und Preis müssen positive Zahlen sein.', 
                                message_type='error'))

    # Verarbeite das Datum
    date_str = request.form['date_bought']
    try:
        date_bought = datetime.strptime(date_str, '%Y-%m-%d') 
    except ValueError:
        return redirect(url_for('tracker.show_portfolio', 
                                message='Fehler: Ungültiges Datumsformat.', 
                                message_type='error'))
        
    # 3. Symbol-Validierung
    if symbol not in COIN_MAPPING:
        return redirect(url_for('tracker.show_portfolio', 
                                message=f'Symbol {symbol} wird nicht unterstützt (Nur BTC, ETH, ADA, SOL).', 
                                message_type='error'))

    # 4. Datenbank-Operation
    try:
        new_tx = Transaction(symbol=symbol, amount=amount, price_usd=price_usd, date_bought=date_bought)
        db.session.add(new_tx)
        db.session.commit()
        
        return redirect(url_for('tracker.show_portfolio', message=f'{symbol} Transaktion erfolgreich hinzugefügt.'))
    
    except Exception as e:
        return redirect(url_for('tracker.show_portfolio', 
                                message=f'Unerwarteter Fehler beim Speichern der Datenbank: {str(e)}', 
                                message_type='error'))