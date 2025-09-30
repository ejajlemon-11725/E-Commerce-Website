# payments/services/bkash.py
import requests
from django.conf import settings

BK = settings.BKASH
BASE = BK["BASE_URL"].rstrip("/")

def _grant_token():
    """
    POST {base}/checkout/token/grant
    Headers: username, password
    Body: {app_key, app_secret}
    Returns: {'id_token': '...', 'token_type': '...', 'expires_in': ...}
    """
    url = f"{BASE}/checkout/token/grant"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "username": BK["USERNAME"],
        "password": BK["PASSWORD"],
    }
    data = {"app_key": BK["APP_KEY"], "app_secret": BK["APP_SECRET"]}
    r = requests.post(url, json=data, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()["id_token"]

def create_payment(amount, invoice_no, callback_url, payer_reference="01700000000"):
    """
    POST {base}/checkout/create with headers:
        authorization: id_token
        x-app-key: APP_KEY
    Body includes currency=BDT, intent=sale, mode=0011 (hosted), callbackURL, merchantInvoiceNumber etc.
    Returns {'paymentID', 'bkashURL', ...}
    """
    id_token = _grant_token()
    url = f"{BASE}/checkout/create"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "authorization": id_token,        # bKash expects id_token here
        "x-app-key": BK["APP_KEY"],
    }
    payload = {
        "mode": "0011",
        "payerReference": payer_reference,
        "callbackURL": callback_url,
        "amount": f"{amount:.2f}",
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": invoice_no,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()

def execute_payment(payment_id):
    """
    POST {base}/checkout/execute with paymentID, same headers.
    Returns execution details with transaction status.
    """
    id_token = _grant_token()
    url = f"{BASE}/checkout/execute"
    headers = {
        "Accept": "application/json",
        "authorization": id_token,
        "x-app-key": BK["APP_KEY"],
    }
    r = requests.post(url, json={"paymentID": payment_id}, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()
