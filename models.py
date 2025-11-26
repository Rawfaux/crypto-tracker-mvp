from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialisiere das SQLAlchemy-Objekt, wird später initialisiert
db = SQLAlchemy()

# Das Datenbank-Modell (Wie die Tabelle aussieht)
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False) # BTC, ETH, etc.
    amount = db.Column(db.Float, nullable=False)
    price_usd = db.Column(db.Float, nullable=False)
    date_bought = db.Column(db.DateTime, nullable=False) 

    def __repr__(self):
        return f'<Transaction {self.symbol}: {self.amount} @ ${self.price_usd}>'