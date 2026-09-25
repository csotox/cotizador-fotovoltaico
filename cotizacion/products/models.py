import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from companies.models import Company


class ProductKind(models.TextChoices):
    PRODUCT = "product", "Producto"
    CONSUMABLE = "consumable", "Consumible"
    SERVICE = "service", "Servicio"


class ProductCategory(models.TextChoices):
    SOLAR_PANEL = "solar_panel", "Panel solar"
    INVERTER = "inverter", "Inversor"
    BATTERY = "battery", "Batería"
    MOUNTING_STRUCTURE = "mounting_structure", "Estructura de montaje"
    CABLE = "cable", "Cable"
    CONNECTOR = "connector", "Conector"
    INSTALLATION = "installation", "Instalación"
    ENGINEERING = "engineering", "Ingeniería"
    OTHER = "other", "Otro"


class ProductUnit(models.TextChoices):
    UNIT = "unit", "Unidad"
    METER = "meter", "Metro"
    SQUARE_METER = "square_meter", "Metro cuadrado"
    HOUR = "hour", "Hora"
    DAY = "day", "Día"
    SERVICE = "service", "Servicio"


class ProductQuerySet(models.QuerySet):
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


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return ProductQuerySet(self.model, using=self._db)

    def dead(self):
        return self.all_with_deleted().dead()


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="products",
    )
    kind = models.CharField(max_length=20, choices=ProductKind.choices)
    category = models.CharField(max_length=30, choices=ProductCategory.choices)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=150, blank=True)
    model = models.CharField(max_length=150, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(
        max_length=20,
        choices=ProductUnit.choices,
        default=ProductUnit.UNIT,
    )
    stock_quantity = models.PositiveIntegerField(null=True, blank=True)
    technical_specs = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ProductManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def clean(self):
        super().clean()
        if self.kind == ProductKind.PRODUCT and self.stock_quantity is None:
            raise ValidationError({"stock_quantity": "El stock es obligatorio para productos."})
        if self.kind != ProductKind.PRODUCT and self.stock_quantity is not None:
            raise ValidationError({"stock_quantity": "El stock no aplica a consumibles o servicios."})

    def __str__(self):
        return self.name
