from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP


def mask_email(email):
    """Utility to mask email address for privacy e.g. a***d@gmail.com"""
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
    return f"{masked_name}@{domain}"


import logging

logger = logging.getLogger(__name__)


def send_otp_email(user, otp_code):
    """Send 6-digit OTP code to user email with console logging fallback."""
    subject = "Verification Code - PersonalityAI"
    message = (
        f"Hello {user.username},\n\n"
        f"Your email verification code for PersonalityAI is: {otp_code}\n\n"
        f"This code is valid for 10 minutes.\n"
        f"If you did not request this account creation, please ignore this email.\n\n"
        f"Best regards,\n"
        f"PersonalityAI Team"
    )
    try:
        send_mail(
            subject,
            message,
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@personalityai.com"),
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.warning(f"Could not send email to {user.email}: {e}. OTP Code: {otp_code}")
        print(f"\n[DEV OTP FALLBACK] Verification OTP for {user.username} ({user.email}): {otp_code}\n")



def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect("register")

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.is_active:
                messages.error(request, "Email is already registered. Please sign in.")
                return redirect("login")
            else:
                # Reuse unverified user account
                user = existing_user
                user.username = username
                user.set_password(password)
                user.save()
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )

        # Generate & send OTP
        otp_obj = EmailOTP.create_or_update_otp(user)
        try:
            send_otp_email(user, otp_obj.otp_code)
        except Exception as e:
            # Fallback for email issues
            pass

        request.session["pending_user_id"] = user.id
        messages.success(
            request,
            f"Verification code sent to {mask_email(email)}. Please enter it below."
        )
        return redirect("verify_otp")

    return render(request, "accounts/register.html")


def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.warning(request, "Please register or log in first.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        return redirect("login")

    if request.method == "POST":
        # Get OTP from form (supports single field or combined 6 boxes)
        digits = [
            request.POST.get(f"otp_{i}", "").strip()
            for i in range(1, 7)
        ]
        entered_otp = "".join(digits) if any(digits) else request.POST.get("otp_code", "").strip()

        try:
            otp_obj = EmailOTP.objects.get(user=user)
        except EmailOTP.DoesNotExist:
            otp_obj = EmailOTP.create_or_update_otp(user)
            send_otp_email(user, otp_obj.otp_code)
            messages.error(request, "New verification code generated. Please try again.")
            return redirect("verify_otp")

        if otp_obj.otp_code == entered_otp and otp_obj.is_valid():
            user.is_active = True
            user.save()
            
            # Auto-login after verification
            login(request, user)
            
            if "pending_user_id" in request.session:
                del request.session["pending_user_id"]
                
            messages.success(request, "Email verified successfully! Welcome to PersonalityAI.")
            return redirect("dashboard_home")
        else:
            if not otp_obj.is_valid():
                messages.error(request, "Verification code has expired. Please click Resend Code.")
            else:
                messages.error(request, "Invalid verification code. Please check and try again.")

    context = {
        "user_email": user.email,
        "masked_email": mask_email(user.email),
    }
    return render(request, "accounts/verify_otp.html", context)


def resend_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        return redirect("login")

    otp_obj = EmailOTP.create_or_update_otp(user)
    try:
        send_otp_email(user, otp_obj.otp_code)
        messages.success(request, f"A new verification code has been sent to {mask_email(user.email)}.")
    except Exception as e:
        messages.error(request, "Failed to send email. Please check your network or try again later.")

    return redirect("verify_otp")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    if request.method == "POST":
        username_or_email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Allow login using username or email (case-insensitive)
        user = User.objects.filter(username__iexact=username_or_email).first()
        if not user:
            user = User.objects.filter(email__iexact=username_or_email).first()

        if user and user.check_password(password):
            if not user.is_active:
                # Unverified user attempt
                request.session["pending_user_id"] = user.id
                otp_obj = EmailOTP.create_or_update_otp(user)
                send_otp_email(user, otp_obj.otp_code)
                messages.warning(
                    request,
                    f"Your email is not verified yet. A verification code has been sent to {mask_email(user.email)}."
                )
                return redirect("verify_otp")

            login(request, user)
            return redirect("dashboard_home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")