from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from companies.mixins import CompanyRequiredMixin
from companies.models import Company

from .forms import ProductForm
from .mixins import ModalFormMixin
from .models import Product


class ProductCompanyMixin(CompanyRequiredMixin):
    pass


class ProductListView(LoginRequiredMixin, ProductCompanyMixin, ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(company=self.get_company()).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.get_company()
        return context


class ProductCreateView(
    LoginRequiredMixin,
    ProductCompanyMixin,
    ModalFormMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Product
    form_class = ProductForm
    template_name = "products/_form.html"
    success_message = "Elemento creado exitosamente."

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
        return reverse("products:detail", kwargs={"uuid": self.object.uuid})


class ProductDetailView(LoginRequiredMixin, ProductCompanyMixin, DetailView):
    model = Product
    template_name = "products/detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        return Product.objects.filter(company=self.get_company())


class ProductUpdateView(
    LoginRequiredMixin,
    ProductCompanyMixin,
    ModalFormMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Product
    form_class = ProductForm
    template_name = "products/_form.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    success_message = "Elemento actualizado exitosamente."

    def get_queryset(self):
        return Product.objects.filter(company=self.get_company())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.get_company()
        return kwargs

    def get_success_url(self):
        return reverse("products:detail", kwargs={"uuid": self.object.uuid})


class ProductDeleteView(LoginRequiredMixin, ProductCompanyMixin, SuccessMessageMixin, DeleteView):
    model = Product
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    http_method_names = ["post"]
    success_message = "Elemento eliminado."

    def get_queryset(self):
        return Product.objects.filter(company=self.get_company())

    def get_success_url(self):
        return reverse("products:list")
