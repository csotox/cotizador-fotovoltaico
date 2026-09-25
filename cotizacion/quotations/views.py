from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from companies.models import Company

from .forms import QuotationForm, QuotationItemForm
from .models import Quotation, QuotationItem, QuotationStatus
from .services import add_quotation_item, delete_quotation_item, update_quotation_item


class QuotationCompanyMixin:
    def get_company(self):
        company = Company.objects.filter(created_by=self.request.user).first()
        if company is None:
            raise Http404
        return company

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied("Un usuario Staff no puede gestionar cotizaciones.")
        return super().dispatch(request, *args, **kwargs)


class QuotationListView(LoginRequiredMixin, QuotationCompanyMixin, ListView):
    model = Quotation
    template_name = "quotations/list.html"
    context_object_name = "quotations"

    def get_queryset(self):
        return Quotation.objects.filter(company=self.get_company()).prefetch_related("items").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.get_company()
        return context


class QuotationCreateView(LoginRequiredMixin, QuotationCompanyMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotations/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.get_company()
        return kwargs

    def form_valid(self, form):
        form.instance.company = self.get_company()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("quotations:detail", kwargs={"uuid": self.object.uuid})


class QuotationDetailView(LoginRequiredMixin, QuotationCompanyMixin, DetailView):
    model = Quotation
    template_name = "quotations/detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        return Quotation.objects.filter(company=self.get_company()).prefetch_related("items")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = context["object"].items.all()
        return context


class QuotationUpdateView(LoginRequiredMixin, QuotationCompanyMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotations/edit_form.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        return Quotation.objects.filter(company=self.get_company())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.get_company()
        return kwargs

    def get_success_url(self):
        return reverse("quotations:detail", kwargs={"uuid": self.object.uuid})


class QuotationDeleteView(
    LoginRequiredMixin,
    QuotationCompanyMixin,
    SuccessMessageMixin,
    DeleteView,
):
    model = Quotation
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    http_method_names = ["post"]
    success_message = "Cotización eliminada."

    def get_queryset(self):
        return Quotation.objects.filter(company=self.get_company())

    def get_success_url(self):
        return reverse("quotations:list")


class QuotationItemCreateView(LoginRequiredMixin, QuotationCompanyMixin, CreateView):
    model = QuotationItem
    form_class = QuotationItemForm
    template_name = "quotations/item_form.html"

    def get_quotation(self):
        if not hasattr(self, "quotation"):
            self.quotation = get_object_or_404(
                Quotation,
                uuid=self.kwargs["uuid"],
                company=self.get_company(),
            )
        return self.quotation

    def get(self, request, *args, **kwargs):
        quotation = self.get_quotation()
        if quotation.status != QuotationStatus.DRAFT:
            raise PermissionDenied("Solo las cotizaciones en borrador pueden agregar productos.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        quotation = self.get_quotation()
        if quotation.status != QuotationStatus.DRAFT:
            raise PermissionDenied("Solo las cotizaciones en borrador pueden agregar productos.")
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance")
        kwargs["company"] = self.get_company()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotation"] = self.get_quotation()
        return context

    def form_valid(self, form):
        quotation = self.get_quotation()
        add_quotation_item(
            quotation=quotation,
            product=form.cleaned_data["product"],
            quantity=form.cleaned_data["quantity"],
        )
        messages.success(self.request, "Producto agregado a la cotización.")
        return redirect("quotations:detail", uuid=quotation.uuid)


class QuotationItemUpdateView(LoginRequiredMixin, QuotationCompanyMixin, UpdateView):
    model = QuotationItem
    form_class = QuotationItemForm
    template_name = "quotations/item_form.html"
    slug_field = "uuid"
    slug_url_kwarg = "item_uuid"

    def get_queryset(self):
        return QuotationItem.objects.filter(
            quotation__uuid=self.kwargs["uuid"],
            quotation__company=self.get_company(),
        ).select_related("quotation", "product")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.quotation.status != QuotationStatus.DRAFT:
            raise PermissionDenied("Solo las cotizaciones en borrador pueden modificar productos.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance")
        kwargs["company"] = self.get_company()
        kwargs["initial"] = {
            "product": self.object.product,
            "quantity": self.object.quantity,
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotation"] = self.object.quotation
        return context

    def form_valid(self, form):
        self.object = update_quotation_item(
            item=self.object,
            product=form.cleaned_data["product"],
            quantity=form.cleaned_data["quantity"],
        )
        messages.success(self.request, "Producto actualizado.")
        return redirect("quotations:detail", uuid=self.object.quotation.uuid)

    def get_success_url(self):
        return reverse("quotations:detail", kwargs={"uuid": self.object.quotation.uuid})


class QuotationItemDeleteView(
    LoginRequiredMixin,
    QuotationCompanyMixin,
    SuccessMessageMixin,
    DeleteView,
):
    model = QuotationItem
    slug_field = "uuid"
    slug_url_kwarg = "item_uuid"
    http_method_names = ["post"]
    success_message = "Producto eliminado de la cotización."

    def get_queryset(self):
        return QuotationItem.objects.filter(
            quotation__uuid=self.kwargs["uuid"],
            quotation__company=self.get_company(),
        ).select_related("quotation")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.quotation.status != QuotationStatus.DRAFT:
            raise PermissionDenied("Solo las cotizaciones en borrador pueden eliminar productos.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        quotation_uuid = self.object.quotation.uuid
        delete_quotation_item(self.object)
        messages.success(self.request, self.success_message)
        return redirect(reverse("quotations:detail", kwargs={"uuid": quotation_uuid}))

    def get_success_url(self):
        return reverse("quotations:detail", kwargs={"uuid": self.kwargs["uuid"]})
