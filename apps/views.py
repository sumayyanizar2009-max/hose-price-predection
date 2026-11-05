import pickle
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import HousePrediction, Feedback


MODEL_PATH = Path(__file__).resolve().parent.parent / "house_price_model.pkl"


def home_view(request):
    return render(request, "apps/home.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([username, email, password, confirm_password]):
            messages.error(request, "Please fill in all fields.")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")

        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")

        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("predict")

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
            login(request, user)
            return redirect("predict")

        messages.error(request, "Invalid username or password.")

    return render(request, "apps/login.html")


@login_required
def predict_view(request):
    predicted_price = None

    if request.method == "POST":
        try:
            area = float(request.POST.get("area", ""))
            bedrooms = int(request.POST.get("bedrooms", ""))
            bathrooms = int(request.POST.get("bathrooms", ""))
            kitchen = int(request.POST.get("kitchen", "1"))
            floors = int(request.POST.get("floors", "1"))
            parking = int(request.POST.get("parking", "0"))

            location = request.POST.get("location", "").strip()
            house_type = request.POST.get("house_type", "")
            furnishing = request.POST.get("furnishing", "")

            house_plan = request.FILES.get("house_plan")

            if area <= 0 or bedrooms <= 0 or bathrooms <= 0:
                raise ValueError("Enter positive area, bedrooms and bathrooms.")

            if kitchen <= 0 or floors <= 0 or parking < 0:
                raise ValueError("Enter valid kitchen, floor and parking values.")

            if not location:
                raise ValueError("Please enter the location.")

            # Validate uploaded house plan
            if house_plan:
                allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
                extension = Path(house_plan.name).suffix.lower()

                if extension not in allowed_extensions:
                    raise ValueError("Upload only JPG, PNG or PDF files.")

                if house_plan.size > 5 * 1024 * 1024:
                    raise ValueError("File size must be below 5 MB.")

            # Load machine learning model
            with open(MODEL_PATH, "rb") as model_file:
                model = pickle.load(model_file)

            # Current model uses only 3 inputs
            prediction = model.predict(
                [[area, bedrooms, bathrooms]]
            )[0]

            predicted_price = round(float(prediction), 2)

            # Save all details in database
            HousePrediction.objects.create(
                user=request.user,
                area=area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                kitchen=kitchen,
                floors=floors,
                parking=parking,
                location=location,
                house_type=house_type,
                furnishing=furnishing,
                house_plan=house_plan,
                predicted_price=predicted_price
            )

            messages.success(request, "Prediction completed successfully!")

        except (ValueError, TypeError) as error:
            messages.error(request, f"Invalid details: {error}")

        except (OSError, pickle.UnpicklingError) as error:
            messages.error(request, f"Model loading error: {error}")

        except Exception as error:
            messages.error(request, f"Prediction error: {error}")

    return render(
        request,
        "apps/predict.html",
        {"predicted_price": predicted_price}
    )


@login_required
def history_view(request):
    predictions = HousePrediction.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "apps/history.html",
        {"predictions": predictions}
    )


@login_required
def delete_history_view(request, pk):
    if request.method == "POST":
        prediction = get_object_or_404(
            HousePrediction,
            pk=pk,
            user=request.user
        )

        if prediction.house_plan:
            prediction.house_plan.delete(save=False)

        prediction.delete()
        messages.success(request, "Prediction deleted successfully.")

    return redirect("history")


@login_required
def clear_history_view(request):
    if request.method == "POST":
        predictions = HousePrediction.objects.filter(user=request.user)

        for prediction in predictions:
            if prediction.house_plan:
                prediction.house_plan.delete(save=False)

        predictions.delete()
        messages.success(request, "History cleared successfully.")

    return redirect("history")


def logout_view(request):
    logout(request)
    return redirect("home")

def learn_more_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        rating = request.POST.get("rating", "")
        message = request.POST.get("message", "").strip()

        if name and rating and message:
            Feedback.objects.create(
                name=name,
                rating=int(rating),
                message=message
            )
            messages.success(request, "Thank you! Your feedback was submitted.")
            return redirect("learn_more")

        messages.error(request, "Please fill in all fields.")

    return render(request, "apps/learn_more.html")