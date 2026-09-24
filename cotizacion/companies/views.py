from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from .forms import CompanyForm
from .models import Company


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = "companies/list.html"
    context_object_name = "companies"

    def get_queryset(self):
        return Company.objects.filter(created_by=self.request.user).order_by("-created_at")


class CompanyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/form.html"
    success_message = "Empresa creada exitosamente."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied("Un usuario Staff no puede crear una empresa.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("companies:detail", kwargs={"uuid": self.object.uuid})


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = "companies/detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        return Company.objects.filter(created_by=self.request.user)