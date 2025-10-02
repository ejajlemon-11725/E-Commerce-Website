# payments/views.py
import uuid
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Payment
from .services import bkash, nagad
from orders.cart import Cart
from orders.models import Order, OrderItem
from django.contrib.auth.decorators import login_required


def _order_amount(order):
    return Decimal(getattr(order, "total", "0.00"))


@login_required
def checkout_view(request):
    from orders.models import Order
    from orders.cart import Cart

    cart = Cart(request)

    if len(cart) == 0:  # <-- check if cart is empty
        # Redirect to cart page if empty
        return redirect('orders:cart_detail')

    # Create order using actual total
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total=cart.get_total()  # <-- CALL the method to get decimal
    )

    amount = order.total
    return render(request, "payments/checkout.html", {"order": order, "amount": amount})


def payment_create(request, order_id):
    return HttpResponse(f"Payment created for order {order_id}")


def payment_success(request):
    return render(request, "payments/success.html")


def payment_fail(request):
    return render(request, "payments/fail.html")


# ---------------- bKash ----------------
def bkash_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    amount = _order_amount(order)
    invoice = f"INV-{order_id}-{uuid.uuid4().hex[:8].upper()}"

    p = Payment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        order=order,
        gateway="bkash",
        amount=amount,
        invoice_no=invoice,
        status="initiated"
    )

    callback_url = request.build_absolute_uri(reverse("payments:bkash_callback"))
    resp = bkash.create_payment(amount=amount, invoice_no=invoice, callback_url=callback_url)
    p.provider_payment_id = resp.get("paymentID", "")
    p.meta = resp
    p.status = "redirected"
    p.save(update_fields=["provider_payment_id", "meta", "status"])
    return redirect(resp["bkashURL"])


@csrf_exempt
def bkash_callback(request):
    payment_id = request.GET.get("paymentID") or request.POST.get("paymentID")
    status = request.GET.get("status") or request.POST.get("status")
    payment = Payment.objects.filter(provider_payment_id=payment_id, gateway="bkash").order_by("-id").first()

    try:
        exec_resp = bkash.execute_payment(payment_id)
        ok = str(exec_resp.get("transactionStatus", "")).lower() in ("completed", "success") or exec_resp.get("statusCode") in ("0000", "000")
        if payment:
            payment.mark("success" if ok else "failed", meta={"callback_status": status, "execute": exec_resp})
        return redirect(settings.PAYMENT_RETURN_SUCCESS_URL if ok else settings.PAYMENT_RETURN_FAIL_URL)
    except Exception as e:
        if payment:
            payment.mark("failed", meta={"error": str(e), "callback_status": status})
        return redirect(settings.PAYMENT_RETURN_FAIL_URL)


# ---------------- Nagad ----------------
def nagad_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    amount = _order_amount(order)
    invoice = f"INV-{order_id}-{uuid.uuid4().hex[:8].upper()}"

    p = Payment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        order=order,
        gateway="nagad",
        amount=amount,
        invoice_no=invoice,
        status="initiated"
    )
    callback_url = settings.NAGAD["CALLBACK_URL"]
    client_ip = request.META.get("REMOTE_ADDR")
    resp = nagad.init_checkout(amount=amount, invoice_number=invoice, client_ip=client_ip)
    p.status = "redirected"
    p.meta = resp
    p.save(update_fields=["status", "meta"])
    return redirect(resp["callBackUrl"])


@csrf_exempt
def nagad_callback(request):
    qs = request.GET.dict()
    ref_id = qs.get("payment_ref_id") or qs.get("paymentRefId") or ""
    order_id = qs.get("order_id") or qs.get("invoice_number")
    pay = Payment.objects.filter(invoice_no=order_id, gateway="nagad").order_by("-id").first()

    try:
        v = nagad.verify(ref_id)
        ok = (v.get("statusCode") == "000" and v.get("status") == "Success" and bool(v.get("issuerPaymentRefNo")))
        if pay:
            pay.provider_payment_id = ref_id
            pay.mark("success" if ok else "failed", meta={"callback": qs, "verify": v})
        return redirect(settings.PAYMENT_RETURN_SUCCESS_URL if ok else settings.PAYMENT_RETURN_FAIL_URL)
    except Exception as e:
        if pay:
            pay.mark("failed", meta={"callback": qs, "error": str(e)})
        return redirect(settings.PAYMENT_RETURN_FAIL_URL)


# ---------------- Stripe ----------------
@csrf_exempt
def stripe_webhook(request):
    return HttpResponse("Stripe webhook received")
