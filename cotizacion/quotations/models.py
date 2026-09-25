import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from companies.models import Company
from customers.models import Customer
from products.models import Product, ProductUnit


class QuotationStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    ISSUED = "issued", "Emitida"
    ACCEPTED = "accepted", "Aceptada"
    REJECTED = "rejected", "Rechazada"


class QuotationQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self, hard=False, **kwargs):
        if hard:
            return super().delete(**kwargs)
        return self.update(deleted_at=timezone.now())

    def hard_delete(self, **kwargs):
        return self.delete(hard=True, **kwargs)


class QuotationManager(models.Manager):
    def get_queryset(self):
        return QuotationQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return QuotationQuerySet(self.model, using=self._db)

    def dead(self):
        return self.all_with_deleted().dead()


class Quotation(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="quotations",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="quotations",
        to_field="uuid",
    )
    status = models.CharField(
        max_length=20,
        choices=QuotationStatus.choices,
        default=QuotationStatus.DRAFT,
    )
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = QuotationManager()

    def clean(self):
        super().clean()
        if self.company_id and self.customer_id and self.customer.company_id != self.company_id:
            raise ValidationError({"customer": "El cliente debe pertenecer a la misma compañía."})

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return f"Cotización {self.uuid}"


class QuotationItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="quotation_items",
        to_field="uuid",
    )
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, choices=ProductUnit.choices)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        errors = {}
        if self.quotation_id and self.product_id and self.product.company_id != self.quotation.company_id:
            errors["product"] = "El producto debe pertenecer a la misma compañía."
        if self.quantity is not None and self.quantity <= 0:
            errors["quantity"] = "La cantidad debe ser mayor que cero."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.product_name
