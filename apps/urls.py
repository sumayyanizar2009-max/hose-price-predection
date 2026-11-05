from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("learn-more/", views.learn_more_view, name="learn_more"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("predict/", views.predict_view, name="predict"),
    path("history/", views.history_view, name="history"),
    path("history/delete/<int:pk>/", views.delete_history_view, name="delete_history"),
    path("history/clear/", views.clear_history_view, name="clear_history"),
    path("logout/", views.logout_view, name="logout"),
]