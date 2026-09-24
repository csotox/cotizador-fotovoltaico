from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import CompanyForm
from .mixins import ModalFormMixin
from .models import Company


class CompanyCreateView(LoginRequiredMixin, ModalFormMixin, SuccessMessageMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/_form.html"
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


class CompanyUpdateView(LoginRequiredMixin, ModalFormMixin, SuccessMessageMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/_form.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    success_message = "Empresa actualizada exitosamente."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied("Un usuario Staff no puede editar una empresa.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Company.objects.filter(created_by=self.request.user)

    def get_success_url(self):
        return reverse("companies:detail", kwargs={"uuid": self.object.uuid})


class CompanyDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Company
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    http_method_names = ["post"]
    success_message = "Empresa eliminada."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied("Un usuario Staff no puede eliminar una empresa.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Company.objects.filter(created_by=self.request.user)

    def get_success_url(self):
        return reverse("home")