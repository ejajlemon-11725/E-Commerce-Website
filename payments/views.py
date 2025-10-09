import uuid
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Payment
from .services import bkash, nagad
from orders.cart import Cart
from orders.models import Order, OrderItem


def _order_amount(order):
    return Decimal(getattr(order, "total", "0.00"))


@login_required
def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('orders:cart_detail')

    # Create order using actual total
    order = Order.objects.create(
        user=request.user,
        total=cart.grand_total
    )
    amount = order.total
    return render(request, "payments/checkout.html", {"order": order, "amount": amount})


def payment_create(request, order_id):
    # This is often where you initiate the payment gateway process
    return HttpResponse(f"Payment created for order {order_id}")


def payment_fail(request):
    return render(request, "payments/fail.html")


# --- CORE PAYMENT SUCCESS HANDLER ---
@login_required
def payment_success_view(request, order_id):
    """
    Handles successful payment, finalizes order status, and sends email.
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status != 'paid':
        order.status = 'paid'
        order.save()

        # Send confirmation email
        try:
            subject = f"Your Payment for Order #{order.id} is Successful"
            message_body = render_to_string('payments/payment_success_email.txt', {
                'user': request.user,
                'order': order,
                'site_name': "Your Shop Name"
            })
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                fail_silently=False,
            )
            messages.success(
                request,
                f"Your payment for Order #{order.id} is successful and a confirmation email has been sent to {order.email}."
            )
        except Exception as e:
            messages.error(
                request,
                f"Payment was successful, but failed to send confirmation email. Error: {e}"
            )
            print(f"Error sending payment success email for Order {order.id}: {e}")
    else:
        messages.success(
            request,
            f"Your payment for Order #{order.id} was already confirmed as successful."
        )

    return render(request, "payments/success.html", {'order': order})


# ---------------- bKash ----------------
def bkash_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    amount = _order_amount(order)
    invoice = f"INV-{order_id}-{uuid.uuid4().hex[:8].upper()}"

    p = Payment.objects.create(
        user=request.user,
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
    order_id = payment.order_id if payment and payment.order else None

    try:
        exec_resp = bkash.execute_payment(payment_id)
        ok = str(exec_resp.get("transactionStatus", "")).lower() in ("completed", "success") or exec_resp.get(
            "statusCode") in ("0000", "000")

        if payment:
            payment.mark("success" if ok else "failed", meta={"callback_status": status, "execute": exec_resp})

        if ok and order_id:
            return redirect(reverse("payments:payment_success", kwargs={'order_id': order_id}))
        else:
            return redirect(settings.PAYMENT_RETURN_FAIL_URL)

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
        user=request.user,
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
    order_invoice = qs.get("order_id") or qs.get("invoice_number")
    pay = Payment.objects.filter(invoice_no=order_invoice, gateway="nagad").order_by("-id").first()
    order_id = pay.order_id if pay and pay.order else None

    try:
        v = nagad.verify(ref_id)
        ok = (v.get("statusCode") == "000" and v.get("status") == "Success" and bool(v.get("issuerPaymentRefNo")))

        if pay:
            pay.provider_payment_id = ref_id
            pay.mark("success" if ok else "failed", meta={"callback": qs, "verify": v})

        if ok and order_id:
            return redirect(reverse("payments:payment_success", kwargs={'order_id': order_id}))
        else:
            return redirect(settings.PAYMENT_RETURN_FAIL_URL)

    except Exception as e:
        if pay:
            pay.mark("failed", meta={"callback": qs, "error": str(e)})
        return redirect(settings.PAYMENT_RETURN_FAIL_URL)


# ---------------- Stripe ----------------
@csrf_exempt
def stripe_webhook(request):
    return HttpResponse("Stripe webhook received")
