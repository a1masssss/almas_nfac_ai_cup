from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView  
from .views import SingUpView


urlpatterns = [
    path("register/", SingUpView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="users/logout.html", next_page='home'), name="logout"),
]