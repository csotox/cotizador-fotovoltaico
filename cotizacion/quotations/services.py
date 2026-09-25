from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from products.models import Product

from .models import Quotation, QuotationItem, QuotationStatus

CENT = Decimal("0.01")


def calculate_subtotal(quantity, unit_price):
    return (Decimal(quantity) * Decimal(unit_price)).quantize(CENT, rounding=ROUND_HALF_UP)


@transaction.atomic
def add_quotation_item(*, quotation, product, quantity):
    locked_quotation = Quotation.objects.select_for_update().get(pk=quotation.pk)
    _ensure_editable(locked_quotation)
    _ensure_available_product(locked_quotation, product)
    item = QuotationItem.objects.create(
        quotation=locked_quotation,
        product=product,
        product_name=product.name,
        product_sku=product.sku,
        unit=product.unit,
        unit_price=product.unit_price,
        quantity=quantity,
        subtotal=calculate_subtotal(quantity, product.unit_price),
    )
    item.full_clean()
    quotation.total = recalculate_quotation_total(locked_quotation)
    quotation.updated_at = timezone.now()
    return item


@transaction.atomic
def update_quotation_item(*, item, product, quantity):
    quotation = Quotation.objects.select_for_update().get(pk=item.quotation_id)
    _ensure_editable(quotation)
    _ensure_available_product(quotation, product)
    item.quotation = quotation
    item.product = product
    item.product_name = product.name
    item.product_sku = product.sku
    item.unit = product.unit
    item.unit_price = product.unit_price
    item.quantity = quantity
    item.subtotal = calculate_subtotal(quantity, product.unit_price)
    item.full_clean()
    item.save()
    recalculate_quotation_total(quotation)
    return item


@transaction.atomic
def delete_quotation_item(item):
    quotation = Quotation.objects.select_for_update().get(pk=item.quotation_id)
    _ensure_editable(quotation)
    item.delete()
    recalculate_quotation_total(quotation)


@transaction.atomic
def recalculate_quotation_total(quotation):
    locked_quotation = Quotation.objects.select_for_update().get(pk=quotation.pk)
    total = QuotationItem.objects.filter(quotation=locked_quotation).aggregate(
        total=Sum("subtotal")
    )["total"] or Decimal("0.00")
    locked_quotation.total = total
    locked_quotation.save(update_fields=["total", "updated_at"])
    quotation.total = total
    quotation.updated_at = timezone.now()
    return total


def _ensure_editable(quotation):
    if quotation.status != QuotationStatus.DRAFT:
        raise ValidationError("Solo las cotizaciones en borrador pueden modificar sus productos.")


def _ensure_available_product(quotation, product):
    if product.company_id != quotation.company_id:
        raise ValidationError("El producto debe pertenecer a la misma compañía.")
    if not product.is_active:
        raise ValidationError("El producto debe estar activo.")
    if not Product.objects.filter(pk=product.pk, deleted_at__isnull=True).exists():
        raise ValidationError("El producto no está disponible.")
