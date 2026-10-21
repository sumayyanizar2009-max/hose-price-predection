from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
import pickle
from pathlib import Path
from .models import HousePrediction

def settings_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "apps/settings.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")


        if not username or not email or not password or not confirm_password:
            messages.error(request, "Please fill in all fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        auth_login(request, user)
        messages.success(request, "Registration successful!")
        return redirect("home")

    return render(request, "apps/register.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
          auth_login(request, user)
          return redirect("home")

        messages.error(request, "Invalid username or password!")

    return render(request, "apps/login.html")

def home_view(request):
    if not request.user.is_authenticated:
        return redirect("login")


    user_predictions = HousePrediction.objects.filter(user=request.user)

    total_predictions = user_predictions.count()

    latest_prediction = user_predictions.order_by("-created_at").first()

    recent_predictions = user_predictions.order_by("-created_at")[:3]

    context = {
    "total_predictions": total_predictions,
    "latest_prediction": latest_prediction,
    "recent_predictions": recent_predictions,
}

    return render(request, "apps/home.html", context)




def predict_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        area = float(request.POST.get("area", 0))
        bedrooms = int(request.POST.get("bedrooms", 0))
        bathrooms = int(request.POST.get("bathrooms", 0))
        location = request.POST.get("location", "").strip()

        if area <= 0 or bedrooms <= 0 or bathrooms <= 0 or not location:
            messages.error(request, "Please enter valid house details.")
            return redirect("predict")

        model_path = Path(__file__).resolve().parent.parent / "house_price_model.pkl"

        with open(model_path, "rb") as file:
            model = pickle.load(file)

        predicted_price = float(
            model.predict([[area, bedrooms, bathrooms]])[0]
        )

        HousePrediction.objects.create(
            user=request.user,
            area=area,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            location=location,
            predicted_price=predicted_price,
        )

        return render(request, "apps/predict.html", {
            "predicted_price": predicted_price,
        })

    return render(request, "apps/predict.html")


def history_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    predictions = HousePrediction.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "apps/history.html", {
        "predictions": predictions,
    })

def logout_view(request):
    logout(request)
    return redirect("login")

