from django import forms
from django.core.exceptions import ValidationError

from .models import Product, ProductCategory, ProductKind, ProductUnit

FORM_CONTROL = "form-control"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "kind",
            "category",
            "name",
            "description",
            "sku",
            "manufacturer",
            "model",
            "unit_price",
            "unit",
            "stock_quantity",
            "technical_specs",
            "is_active",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "technical_specs": forms.Textarea(attrs={"rows": 4}),
            "is_active": forms.CheckboxInput(),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None and not self.instance.pk:
            self.instance.company = company
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", FORM_CONTROL)
        self.fields["kind"].choices = ProductKind.choices
        self.fields["category"].choices = ProductCategory.choices
        self.fields["unit"].choices = ProductUnit.choices
        self.fields["stock_quantity"].required = False
        kind = self.data.get("kind") if self.is_bound else self.instance.kind
        if kind != ProductKind.PRODUCT:
            self.fields["stock_quantity"].disabled = True

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip()
        if not sku:
            return ""
        queryset = Product.objects.filter(
            company=self.instance.company,
            sku__iexact=sku,
        )
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe un elemento con este SKU en la compañía.")
        return sku

    def clean_technical_specs(self):
        value = self.cleaned_data.get("technical_specs")
        if value in (None, ""):
            return {}
        if isinstance(value, dict):
            return value
        import json

        try:
            specs = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValidationError("Ingresa especificaciones técnicas en formato JSON.") from exc
        if not isinstance(specs, dict):
            raise ValidationError("Las especificaciones técnicas deben ser un objeto JSON.")
        return specs

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get("kind")
        stock_quantity = cleaned_data.get("stock_quantity")
        if kind in (ProductKind.CONSUMABLE, ProductKind.SERVICE):
            cleaned_data["stock_quantity"] = None
        return cleaned_data
