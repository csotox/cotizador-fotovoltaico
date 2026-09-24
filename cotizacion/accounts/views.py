from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from companies.models import Company

from .forms import RegistrationForm


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = "accounts/signup.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("login")
    success_message = "Registro exitoso. Ahora puedes iniciar sesión."


@login_required
def home(request):
    companies = Company.objects.none()
    if not request.user.is_staff:
        companies = Company.objects.filter(created_by=request.user).order_by("-created_at")
    return render(request, "accounts/home.html", {"companies": companies})