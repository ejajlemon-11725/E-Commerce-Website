# payments/services/nagad.py
from django.conf import settings
from nagadpy import NagadPayment, NagadPaymentVerify

def init_checkout(amount, invoice_number, client_ip):
    ng = NagadPayment(
        merchant_id=settings.NAGAD["MERCHANT_ID"],
        callback_url=settings.NAGAD["CALLBACK_URL"],
        base_url=settings.NAGAD["BASE_URL"],   # sandbox-ssl.mynagad.com:10061 (sandbox)
        public_key=settings.NAGAD["PUBLIC_KEY"],
        private_key=settings.NAGAD["PRIVATE_KEY"],
        client_ip_address=client_ip or "127.0.0.1",
    )
    # Returns {'callBackUrl': 'https://sandbox-ssl.mynagad.com:10061/check-out/....', 'status': 'Success'}
    return ng.checkout_process(amount=f"{amount:.2f}", invoice_number=invoice_number)

def verify(payment_ref_id):
    # Ask Nagad for final verification by the reference id from callback query params
    v = NagadPaymentVerify(base_url=settings.NAGAD["BASE_URL"])
    return v.verify_payment(payment_ref_id)
