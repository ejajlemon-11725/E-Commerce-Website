from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout
from .forms import SignUpForm
from .models import CustomUser

from django.core.mail import send_mail
from django.http import HttpResponse

def send_test_email(request):
    subject = 'Test Email from Django'
    message = 'Hello! This is a test email sent from Django.'
    from_email = None  # Uses DEFAULT_FROM_EMAIL from settings.py
    recipient_list = ['recipient-email@example.com']  # Replace with your email

    try:
        send_mail(subject, message, from_email, recipient_list)
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {e}")


# ------------------ USER SIGNUP (Email Verification) ------------------
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.is_active = False  # user will be inactive until they verify email
            user.save()

            # Build activation email
            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            message = render_to_string("accounts/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })

            # Send email
            try:
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.content_subtype = "html"  # to render HTML email
                email.send()
                messages.success(request, "✅ Please check your email to activate your account.")
            except Exception as e:
                messages.error(request, f"❌ Email sending failed: {e}")

            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


# ------------------ EMAIL ACTIVATION ------------------
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "🎉 Your account has been activated! You can now log in.")
        return redirect("login")
    else:
        messages.error(request, "⚠️ Activation link is invalid or expired.")
        return redirect("signup")


# ------------------ CUSTOM LOGIN (Case-insensitive) ------------------
def custom_login(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(username__iexact=username_or_email)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email__iexact=username_or_email)
            except CustomUser.DoesNotExist:
                user = None

        if user is not None and user.check_password(password):
            if user.is_active:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "⚠️ Account not active. Please check your email.")
        else:
            messages.error(request, "❌ Invalid username/email or password.")

    return render(request, "accounts/login.html")


# ------------------ LOGOUT ------------------
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
