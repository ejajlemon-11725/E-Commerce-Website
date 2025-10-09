from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm
from .models import CustomUser
from .tokens import account_activation_token

# Signup & activation remain the same
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()  # normalize username
            user.email = user.email.lower()        # normalize email
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = "Activate your account"
            message = render_to_string("accounts/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            messages.info(request, "Please check your email to activate your account.")
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated!")
        return redirect("home")
    else:
        return render(request, "accounts/activation_invalid.html")


# --------- Custom login view to fix case-sensitivity ---------
def custom_login(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username").lower()  # lowercase input
        password = request.POST.get("password")

        # Try to get the user by username OR email (case-insensitive)
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
                messages.error(request, "Account is not active. Please check your email.")
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, "accounts/login.html")


# --------- Custom Logout View ---------
def custom_logout(request):
    # Log out the user using the built-in function
    logout(request)

    # Add a success message
    messages.success(request, "You have been logged out successfully!")

    # Redirect to the home page or login page
    return redirect("home")  # Or return redirect("login")