from django.urls import path
from . import views

urlpatterns = [
path("", views.home_view, name="home"),
path("register/", views.register_view, name="register"),
path("login/", views.login_view, name="login"),
path("home/", views.home_view, name="home"),
path("predict/", views.settings_view, name="settings"),
path("predict/", views.predict_view, name="predict"),
path("history/", views.history_view, name="history"),
path("logout/", views.logout_view, name="logout"),
]
