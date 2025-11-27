from flask import Flask
import os
from datetime import datetime
# NEU: Verwende relative Imports
from models import db, Transaction 
from routes import tracker_blueprint 
from config import COIN_MAPPING


def create_app():
    # Erstelle die Flask App
    app = Flask(__name__)

    # --- Datenbank Konfiguration ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tracker.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialisiere die Datenbank mit der App
    db.init_app(app) 

    # Registriere den Blueprint, der alle Routen enthält
    app.register_blueprint(tracker_blueprint) 
    
    return app
    
# 1. Erstelle die App-Instanz auf der obersten Ebene, damit Gunicorn sie findet.
# Gunicorn ruft 'app' auf und erhält das fertige Flask-Objekt.
app = create_app()

# Dies ist der Standardstartpunkt
if __name__ == '__main__':
    app.run(debug=True)
    
    # Dieser Block muss vor dem ersten App-Start ausgeführt werden
    with app.app_context():
        # Erstellt die Datenbank-Tabelle, falls sie nicht existiert
        db.create_all() 
        
        # Füge die Demo-Transaktion nur ein, wenn die Tabelle leer ist
        if not Transaction.query.first():
            print("Füge BTC- und ETH-Demo-Transaktionen ein.")
            db.session.add(Transaction(symbol='BTC', amount=0.5, price_usd=30000.0, date_bought=datetime(2023, 1, 15)))
            db.session.add(Transaction(symbol='ETH', amount=2.0, price_usd=2000.0, date_bought=datetime(2023, 5, 20)))
            db.session.commit()
            
    app.run(debug=True)