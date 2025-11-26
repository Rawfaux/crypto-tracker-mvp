# init_db.py
from app import create_app
from models import db, Transaction
from datetime import datetime

# App erstellen und Kontext aktivieren
app = create_app()

with app.app_context():
    # Löscht alte Tabellen und erstellt sie neu (Vorsicht im Live-Betrieb!)
    # db.drop_all() 
    
    # Erstellt die Datenbank-Tabelle, falls sie nicht existiert
    db.create_all() 
    
    # Füge die Demo-Transaktion nur ein, wenn die Tabelle leer ist
    if not Transaction.query.first():
        print("Füge Demo-Transaktionen ein.")
        db.session.add(Transaction(symbol='BTC', amount=0.5, price_usd=30000.0, date_bought=datetime(2023, 1, 15)))
        db.session.add(Transaction(symbol='ETH', amount=2.0, price_usd=2000.0, date_bought=datetime(2023, 5, 20)))
        db.session.commit()
    
    print("Datenbank initialisiert.")