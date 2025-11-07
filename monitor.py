import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import csv
import os
import sys

ORIGIN = "CGH"
DEST = "BSB"
DATE = "2025-11-25"
THRESHOLD = 25000

def send_email(price):
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL_TO = os.getenv("EMAIL_TO")
    if not (EMAIL_FROM and EMAIL_PASS and EMAIL_TO):
        print("Email env vars not set")
        return

    msg = MIMEText(f"Preço caiu! {price} milhas no trecho {ORIGIN}->{DEST} em {DATE}")
    msg['Subject'] = "Alerta Smiles"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASS)
            server.send_message(msg)
        print("Email enviado.")
    except Exception as e:
        print("Erro ao enviar email:", e)

def log_price(price):
    header_needed = False
    try:
        with open("prices.csv", "r"):
            pass
    except FileNotFoundError:
        header_needed = True

    with open("prices.csv", "a") as f:
        if header_needed:
            f.write("date,price\n")
        f.write(f"{datetime.utcnow().isoformat()},{price}\n")

def get_price():
    url = f"https://api.smiles.com.br/v2/flights?origin={ORIGIN}&destination={DEST}&departureDate={DATE}&adults=1"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("Erro requisitando Smiles:", e)
        return None

    offers = data.get("data") or []
    miles = []
    for o in offers:
        # adapt if estrutura for diferente
        if isinstance(o, dict) and "miles" in o:
            miles.append(o["miles"])
    if not miles:
        print("Nenhuma oferta encontrada ou formato inesperado.")
        return None
    best = min(miles)
    return best

if __name__ == "__main__":
    price = get_price()
    if price is None:
        sys.exit(0)
    print("Preço atual (milhas):", price)
    log_price(price)
    if price < THRESHOLD:
        send_email(price)
