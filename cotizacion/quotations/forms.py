from django import forms

from customers.models import Customer
from products.models import Product

from .models import Quotation

FORM_CONTROL = "form-control"


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ("customer", "status", "notes")
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        if company is not None and not self.instance.pk:
            self.instance.company = company
            self.fields.pop("status")
        if company is not None:
            self.fields["customer"].queryset = Customer.objects.filter(company=company)
        for field in self.fields.values():
            field.widget.attrs["class"] = FORM_CONTROL


class QuotationItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), to_field_name="uuid")
    quantity = forms.DecimalField(
        decimal_places=3,
        min_value=0.001,
        widget=forms.NumberInput(attrs={"step": "0.001", "min": "0.001"}),
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.fields["product"].queryset = Product.objects.filter(
                company=company,
                is_active=True,
            )
        for field in self.fields.values():
            field.widget.attrs["class"] = FORM_CONTROL
