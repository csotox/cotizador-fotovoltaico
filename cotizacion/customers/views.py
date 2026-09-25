from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from companies.mixins import CompanyRequiredMixin
from companies.models import Company

from .forms import CustomerForm
from .mixins import ModalFormMixin
from .models import Customer


class CustomerCompanyMixin(CompanyRequiredMixin):
    pass


class CustomerListView(LoginRequiredMixin, CustomerCompanyMixin, ListView):
    model = Customer
    template_name = "customers/list.html"
    context_object_name = "customers"

    def get_queryset(self):
        return Customer.objects.filter(company=self.get_company()).order_by("-created_at")


class CustomerCreateView(
    LoginRequiredMixin,
    CustomerCompanyMixin,
    ModalFormMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/_form.html"
    success_message = "Cliente creado exitosamente."

    def dispatch(self, request, *args, **kwargs):
        if self.get_company() is None:
            from django.shortcuts import redirect

            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.get_company()
        return kwargs

    def form_valid(self, form):
        form.instance.company = self.get_company()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("customers:detail", kwargs={"uuid": self.object.uuid})


class CustomerDetailView(LoginRequiredMixin, CustomerCompanyMixin, DetailView):
    model = Customer
    template_name = "customers/detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        return Customer.objects.filter(company=self.get_company())


class CustomerUpdateView(
    LoginRequiredMixin,
    CustomerCompanyMixin,
    ModalFormMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Customer
    form_class = CustomerForm
    template_name = "customers/_form.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    success_message = "Cliente actualizado exitosamente."

    def get_queryset(self):
        return Customer.objects.filter(company=self.get_company())

    def get_success_url(self):
        return reverse("customers:detail", kwargs={"uuid": self.object.uuid})


class CustomerDeleteView(LoginRequiredMixin, CustomerCompanyMixin, SuccessMessageMixin, DeleteView):
    model = Customer
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    http_method_names = ["post"]
    success_message = "Cliente eliminado."

    def get_queryset(self):
        return Customer.objects.filter(company=self.get_company())

    def get_success_url(self):
        return reverse("customers:list")
