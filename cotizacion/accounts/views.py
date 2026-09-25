from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from companies.models import Company
from customers.models import Customer
from products.models import Product
from quotations.models import Quotation, QuotationStatus

from .forms import RegistrationForm


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = "accounts/signup.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("login")
    success_message = "Registro exitoso. Ahora puedes iniciar sesión."


@login_required
def home(request):
    if request.user.is_staff:
        return render(request, "accounts/home.html", {"companies": Company.objects.none()})

    company = Company.objects.filter(created_by=request.user).order_by("-created_at").first()
    if company is None:
        return render(request, "accounts/home.html", {"companies": Company.objects.none()})

    quotations = Quotation.objects.filter(company=company)
    metrics = {
        "draft": quotations.filter(status=QuotationStatus.DRAFT).count(),
        "issued": quotations.filter(status=QuotationStatus.ISSUED).count(),
        "accepted": quotations.filter(status=QuotationStatus.ACCEPTED).count(),
        "total": quotations.aggregate(value=Sum("total"))["value"] or Decimal("0"),
    }
    recent_quotations = quotations.select_related("customer").prefetch_related("items")[:5]
    customer_count = Customer.objects.filter(company=company).count()
    product_count = Product.objects.filter(company=company).count()
    context = {
        "companies": Company.objects.filter(created_by=request.user),
        "company": company,
        "metrics": metrics,
        "recent_quotations": recent_quotations,
        "customer_count": customer_count,
        "product_count": product_count,
        "next_step": "Agrega un cliente" if customer_count == 0 else "Carga un producto" if product_count == 0 else "Crear cotización",
    }
    return render(request, "accounts/home.html", context)
